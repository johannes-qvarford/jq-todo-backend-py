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


@dataclasses.dataclass
class Todo:
    title: str


@dataclasses.dataclass
class CreatedTodo(Todo):
    id: uuid.UUID = dataclasses.field(compare=False)
    completed: bool = False
    url: str = dataclasses.field(init=False, compare=False)

    def __post_init__(self):
        self.url = f'http://localhost:5000/{self.id}'

    @staticmethod
    def from_dict(d):
        no_generated_fields = {k: v for k, v in d.items() if k not in ['url']}
        return CreatedTodo(**no_generated_fields)

    @staticmethod
    def from_todo(todo):
        return CreatedTodo(id=uuid.uuid4(), **todo.__dict__)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        return super().default(o)


todosMap = {}


def todos():
    ts = todosMap[flask.current_app] if flask.current_app in todosMap else []
    todosMap[flask.current_app] = ts
    return ts


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


@blueprint.route('/<uuid:id>', methods=['GET'])
def get(id):
    ts = todos()
    matching_todos = [t for t in ts if t.id == id]
    return matching_todos[0].__dict__ if len(matching_todos) > 0 else abort(404)
