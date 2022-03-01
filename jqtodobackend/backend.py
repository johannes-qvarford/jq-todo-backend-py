import uuid

from fastapi import FastAPI, Depends

from jqtodobackend.models import Todo, CreatedTodo, TodoChanges
from jqtodobackend.repository import TodoRepository

app = FastAPI()


@app.get("/")
def get_all(repo: TodoRepository = Depends(TodoRepository)):
    ts = repo.all()
    return ts


@app.delete("/")
def delete_all(repo: TodoRepository = Depends(TodoRepository)):
    repo.clear()


@app.post("/", response_model=CreatedTodo)
def post(
    todo: Todo,
    repo: TodoRepository = Depends(TodoRepository),
):
    created = CreatedTodo.from_todo(todo)
    repo.insert(created)
    return created


@app.get("/{_id}", response_model=CreatedTodo)
def get(
    _id: uuid.UUID,
    repo: TodoRepository = Depends(TodoRepository),
):
    return repo.find(_id).as_successful_http_response_model()


@app.patch("/{_id}")
def patch(
    _id: uuid.UUID,
    todo_changes: TodoChanges,
    repo: TodoRepository = Depends(TodoRepository),
):
    repo.patch(_id, todo_changes)


@app.delete("/{_id}")
def delete(
    _id: uuid.UUID,
    repo: TodoRepository = Depends(TodoRepository),
):
    repo.delete(_id)
