import uuid

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from jqtodobackend.db import (
    find_todo,
    patch_todo,
    remove_todo,
    get_db,
)
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


@app.patch("/{_id}", response_model=CreatedTodo)
def patch(_id: uuid.UUID, todo_changes: TodoChanges, db: Session = Depends(get_db)):
    todo = find_todo(db, _id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    patch_todo(db, _id, todo_changes)
    return todo


@app.delete("/{_id}")
def delete(_id: uuid.UUID, db: Session = Depends(get_db)):
    todo = find_todo(db, _id)
    if todo:
        remove_todo(db, _id)
