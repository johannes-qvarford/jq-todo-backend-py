from fastapi import Depends, HTTPException

from jqtodobackend.db import *


class TodoQueryResult:
    def __init__(self, todo):
        self._todo = todo

    def as_successful_http_response_model(self):
        return self._todo


class MissingTodoQueryResult:
    def as_successful_http_response_model(self):
        raise HTTPException(status_code=404, detail="Todo not found")


class TodoRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    def all(self):
        return todos(self.session)

    def clear(self):
        clear_todos(self.session)

    def insert(self, todo):
        insert_todo(self.session, todo)

    def find(self, _id):
        todo = find_todo(self.session, _id)
        return TodoQueryResult(todo) if todo is not None else MissingTodoQueryResult()
