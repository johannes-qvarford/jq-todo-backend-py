from fastapi import Depends

from jqtodobackend.db import *


class TodoRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    def all(self):
        return todos(self.session)

    def clear(self):
        clear_todos(self.session)

    def insert(self, todo):
        insert_todo(self.session, todo)
