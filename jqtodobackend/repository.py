from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from jqtodobackend.db import *


class QueryResult:
    @staticmethod
    def of(session, obj: Todo | None):
        return (
            TodoQueryResult(session, obj)
            if obj is not None
            else MISSING_TODO_QUERY_RESULT
        )


class TodoQueryResult:
    def __init__(self, session, todo: Todo):
        self.session = session
        self._todo = todo

    def as_http_response(self):
        return JSONResponse(jsonable_encoder(self._todo.as_created_todo))


class MissingTodoQueryResult:
    @staticmethod
    def as_http_response():
        return JSONResponse(status_code=404, content={"detail": "Todo not found"})


MISSING_TODO_QUERY_RESULT = MissingTodoQueryResult()


class TodoRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def all(self):
        return [
            row.as_created_todo
            for row in self.session.execute(select(Todo)).scalars().all()
        ]

    def clear(self):
        self.session.query(Todo).delete()
        self.session.commit()

    def insert(self, created: CreatedTodo):
        self.session.add(Todo.from_created_todo(created))
        self.session.commit()

    def find(self, _id):
        return QueryResult.of(
            session=self.session, obj=self.session.get(Todo, str(_id))
        )

    def patch(self, _id, todo_changes):
        self.session.execute(
            update(Todo)
            .where(Todo.id == str(_id))
            .values(**{k: v for k, v in todo_changes if v is not None})
        )
        self.session.commit()

    def delete(self, _id):
        self.session.execute(delete(Todo).where(Todo.id == str(_id)))
        self.session.commit()
