from fastapi import Depends

from jqtodobackend.db import *


class TodoRepository:
    def __init__(self, session=Depends(get_db)):
        self.session = session

    def all(self):
        return todos(self.session)
