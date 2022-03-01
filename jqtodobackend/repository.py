from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from jqtodobackend.db import *


class TodoQueryResult:
    def __init__(self, session, todo):
        self.session = session
        self._todo = todo

    def as_http_response(self):
        return JSONResponse(jsonable_encoder(self._todo))

    def patch(self, todo_changes):
        patch_todo(self.session, self._todo.id, todo_changes)

    def delete(self):
        self.session.query(Todo).filter_by(id=str(self._todo.id)).delete()
        self.session.commit()


class MissingTodoQueryResult:
    @staticmethod
    def as_http_response():
        return JSONResponse(status_code=404, content={"detail": "Todo not found"})

    def patch(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


MISSING_TODO_QUERY_RESULT = MissingTodoQueryResult()


class TodoRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def all(self):
        return [row.as_created_todo for row in self.session.query(Todo).all()]

    def clear(self):
        self.session.query(Todo).delete()
        self.session.commit()

    def insert(self, created: CreatedTodo):
        self.session.add(Todo.from_created_todo(created))
        self.session.commit()

    def find(self, _id):
        found_todos = [
            x.as_created_todo for x in self.session.query(Todo).filter_by(id=str(_id))
        ]

        return (
            TodoQueryResult(self.session, found_todos[0])
            if len(found_todos) > 0
            else MISSING_TODO_QUERY_RESULT
        )

    def patch(self, _id, todo_changes):
        self.find(_id).patch(todo_changes)

    def delete(self, _id):
        self.find(_id).delete()
