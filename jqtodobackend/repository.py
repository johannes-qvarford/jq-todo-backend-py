from uuid import UUID
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import insert, select, update, delete
from sqlalchemy.engine import Connection, Row
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from starlette.responses import JSONResponse
from jqtodobackend.db import TTodo, get_connection

from jqtodobackend.models import CreatedTodo


def _as_created_todo(self: dict):
    d = dict(self)
    d["id"] = UUID(d["id"])
    model = CreatedTodo(**d)
    model.update_url()
    return model


def _from_created_todo(created) -> dict:
    schema = created.dict(exclude={"url"})
    schema["id"] = str(schema["id"])
    return schema


class QueryResult:
    @staticmethod
    def of(obj: Row | None):
        return TodoQueryResult(obj) if obj is not None else MISSING_TODO_QUERY_RESULT


class TodoQueryResult:
    def __init__(self, todo):
        self._todo = todo

    def as_http_response(self):
        return JSONResponse(jsonable_encoder(_as_created_todo(self._todo._mapping)))


class MissingTodoQueryResult:
    @staticmethod
    def as_http_response():
        return JSONResponse(status_code=404, content={"detail": "Todo not found"})


MISSING_TODO_QUERY_RESULT = MissingTodoQueryResult()


class TodoRepository:
    def __init__(self, connection: Connection = Depends(get_connection)):
        self.connection = connection

    def all(self):
        conn = self.connection
        return [_as_created_todo(row._mapping) for row in conn.execute(select(TTodo))]

    def clear(self):
        conn = self.connection
        with conn.begin():
            conn.execute(delete(TTodo))

    def insert(self, created: CreatedTodo):
        conn = self.connection
        with conn.begin():
            conn.execute(insert(TTodo).values(**_from_created_todo(created)))

    def find(self, _id):
        conn = self.connection
        obj = conn.execute(select(TTodo).where(TTodo.c.id == str(_id))).first()
        return QueryResult.of(obj)

    def patch(self, _id, todo_changes):
        conn = self.connection
        with conn.begin():
            conn.execute(
                update(TTodo)
                .where(TTodo.c.id == str(_id))
                .values(**{k: v for k, v in todo_changes if v is not None})
            )

    def delete(self, _id):
        conn = self.connection
        with conn.begin():
            conn.execute(delete(TTodo).where(TTodo.c.id == str(_id)))
