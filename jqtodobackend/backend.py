from typing import List
from uuid import UUID

from fastapi import FastAPI, Depends

from jqtodobackend.models import Todo, CreatedTodo, TodoChanges
from jqtodobackend.repository import TodoRepository

app = FastAPI()


@app.get("/", response_model=List[CreatedTodo])
def get_all(repo: TodoRepository = Depends(TodoRepository)):
    ts = repo.all()
    return ts


@app.delete("/")
def delete_all(repo: TodoRepository = Depends(TodoRepository)):
    repo.clear()


@app.post("/", response_model=CreatedTodo)
def post(todo: Todo, repo: TodoRepository = Depends(TodoRepository)):
    created = CreatedTodo.from_todo(todo)
    repo.insert(created)
    return created


@app.get(
    "/{_id}",
    response_model=CreatedTodo,
    responses={404: {"description": "Todo could not be found"}},
)
def get(_id: UUID, repo: TodoRepository = Depends(TodoRepository)):
    return repo.find(_id).as_http_response()


@app.patch("/{_id}")
def patch(
    _id: UUID, todo_changes: TodoChanges, repo: TodoRepository = Depends(TodoRepository)
):
    repo.patch(_id, todo_changes)


@app.delete("/{_id}")
def delete(_id: UUID, repo: TodoRepository = Depends(TodoRepository)):
    repo.delete(_id)
