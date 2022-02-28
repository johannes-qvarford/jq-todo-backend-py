import dataclasses
import json
import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Todo(BaseModel):
    title: str
    order: Optional[int] = None


class CreatedTodo(BaseModel):
    title: str
    id: uuid.UUID
    url: Optional[str] = None
    completed: bool = False
    order: Optional[int] = None

    def update_url(self):
        self.url = f"http://localhost:5000/{self.id}"

    @staticmethod
    def from_dict(d):
        no_generated_fields = {k: v for k, v in d.items() if k not in ["url"]}
        return CreatedTodo(**no_generated_fields)

    @staticmethod
    def from_todo(todo):
        created = CreatedTodo(id=uuid.uuid4(), **todo.__dict__)
        created.update_url()
        return created

    def apply_changes(self, changes):
        for k, v in changes.__dict__.items():
            self.__dict__[k] = v if v else self.__dict__[k]

    def __eq__(self, other):
        ignore = ["id", "url"]
        for k in vars(self).keys():
            if k in ignore:
                continue
            if self.__dict__[k] != other.__dict__[k]:
                return False
        return True


class TodoChanges(BaseModel):
    title: str | None = None
    completed: bool | None = None
    order: int | None = None


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


def find_todo(_id):
    matching_todos = [t for t in todos() if t.id == _id]
    return matching_todos[0] if len(matching_todos) > 0 else None


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        return super().default(o)


todos_map: list[CreatedTodo] = []


def todos() -> list[CreatedTodo]:
    return todos_map
