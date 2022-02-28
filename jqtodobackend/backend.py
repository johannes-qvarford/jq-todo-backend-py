import uuid
from fastapi import FastAPI, HTTPException
from jqtodobackend.db import todos, find_todo
from jqtodobackend.models import Todo, CreatedTodo, TodoChanges

app = FastAPI()


@app.get("/")
def get_all():
    ts = todos()
    return ts


@app.delete("/")
def delete_all():
    ts = todos()
    ts.clear()


@app.post("/")
def post(todo: Todo):
    ts = todos()
    created = CreatedTodo.from_todo(todo)
    ts.append(created)
    return created.__dict__


@app.get("/{_id}")
def get(_id: uuid.UUID):
    todo = find_todo(_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo.__dict__


@app.patch("/{_id}")
def patch(_id: uuid.UUID, todo_changes: TodoChanges):
    todo = find_todo(_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.apply_changes(todo_changes)
    return todo.__dict__


@app.delete("/{_id}")
def delete(_id: uuid.UUID):
    todo = find_todo(_id)
    if todo:
        todos().remove(todo)
