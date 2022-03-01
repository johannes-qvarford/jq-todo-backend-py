from fastapi import Depends, HTTPException

from jqtodobackend.db import *


class TodoQueryResult:
    def __init__(self, session, todo):
        self.session = session
        self._todo = todo

    def as_successful_http_response_model(self):
        return self._todo

    def patch(self, todo_changes):
        patch_todo(self.session, self._todo.id, todo_changes)

    def delete(self):
        remove_todo(self.session, self._todo.id)


class MissingTodoQueryResult:
    def as_successful_http_response_model(self):
        raise HTTPException(status_code=404, detail="Todo not found")

    def patch(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


class TodoRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    def all(self):
        return [row.as_created_todo for row in self.session.query(Todo).all()]

    def clear(self):
        self.session.query(Todo).delete()
        self.session.commit()

    def insert(self, todo):
        insert_todo(self.session, todo)

    def find(self, _id):
        todo = find_todo(self.session, _id)
        return (
            TodoQueryResult(self.session, todo)
            if todo is not None
            else MissingTodoQueryResult()
        )

    def patch(self, _id, todo_changes):
        self.find(_id).patch(todo_changes)

    def delete(self, _id):
        self.find(_id).delete()
