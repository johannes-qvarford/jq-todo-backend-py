import dataclasses
import json
import uuid

import flask
from flask import Flask, Blueprint, request, abort


def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    return app


blueprint = Blueprint('', __name__)


@blueprint.route('/')
def get_all():
    ts = todos()
    return json.dumps([t for t in ts], cls=EnhancedJSONEncoder)


@blueprint.route('/', methods=['DELETE'])
def delete_all():
    ts = todos()
    ts.clear()
    return ''


@blueprint.route('/', methods=['POST'])
def post():
    ts = todos()
    todo = CreatedTodo.from_todo(Todo(**request.json))
    ts.append(todo)
    return todo.__dict__


@blueprint.route('/<uuid:_id>', methods=['GET'])
def get(_id):
    todo = find_todo(_id)
    return todo.__dict__ if todo else abort(404)


@blueprint.route('/<uuid:_id>', methods=['PATCH'])
def patch(_id):
    todo = find_todo(_id)
    if todo:
        todo.apply_changes(TodoChanges(**request.json))
        return todo.__dict__
    return abort(404)


@blueprint.route('/<uuid:_id>', methods=['DELETE'])
def delete(_id):
    todo = find_todo(_id)
    if todo:
        todos().remove(todo)
    return ''


def find_todo(_id):
    matching_todos = [t for t in todos() if t.id == _id]
    return matching_todos[0] if len(matching_todos) > 0 else None


@dataclasses.dataclass
class Todo:
    title: str
    order: int | None = None


@dataclasses.dataclass
class CreatedTodo:
    title: str
    id: uuid.UUID = dataclasses.field(compare=False)
    url: str = dataclasses.field(init=False, compare=False)
    completed: bool = False
    order: int | None = None

    def __post_init__(self):
        self.url = f'http://localhost:5000/{self.id}'

    @staticmethod
    def from_dict(d):
        no_generated_fields = {k: v for k, v in d.items() if k not in ['url']}
        return CreatedTodo(**no_generated_fields)

    @staticmethod
    def from_todo(todo):
        return CreatedTodo(id=uuid.uuid4(), **todo.__dict__)

    def apply_changes(self, changes):
        for k, v in changes.__dict__.items():
            self.__dict__[k] = v if v else self.__dict__[k]


@dataclasses.dataclass
class TodoChanges:
    title: str | None = None
    completed: bool | None = None
    order: int | None = None


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        return super().default(o)


todosMap = {}


def todos() -> list[CreatedTodo]:
    ts = todosMap[flask.current_app] if flask.current_app in todosMap else []
    todosMap[flask.current_app] = ts
    return ts
