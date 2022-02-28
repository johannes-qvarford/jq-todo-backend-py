import uuid

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from jqtodobackend.db import (
    todos,
    find_todo,
    clear_todos,
    insert_todo,
    SessionLocal,
    patch_todo,
    remove_todo,
)
from jqtodobackend.models import Todo, CreatedTodo, TodoChanges

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_all(db: Session = Depends(get_db)):
    ts = todos(db)
    return ts


@app.delete("/")
def delete_all(db: Session = Depends(get_db)):
    clear_todos(db)


@app.post("/", response_model=CreatedTodo)
def post(todo: Todo, db: Session = Depends(get_db)):
    created = CreatedTodo.from_todo(todo)
    insert_todo(db, created)
    return created


@app.get("/{_id}", response_model=CreatedTodo)
def get(_id: uuid.UUID, db: Session = Depends(get_db)):
    todo = find_todo(db, _id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


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
