import dataclasses
import json

import flask
from flask import Flask, Blueprint, request


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
    completed: bool = False

    @staticmethod
    def from_todo(todo):
        return CreatedTodo(**todo.__dict__)


todosMap = {}


def todos():
    ts = todosMap[flask.current_app] if flask.current_app in todosMap else []
    todosMap[flask.current_app] = ts
    return ts


@blueprint.route('/')
def get_all():
    ts = todos()
    return json.dumps([t.__dict__ for t in ts])


@blueprint.route('/', methods=['DELETE'])
def delete_all():
    ts = todos()
    ts.clear()
    return ''


@blueprint.route('/', methods=['POST'])
def post():
    ts = todos()
    todo = CreatedTodo(**request.json)
    ts.append(todo)
    return todo.__dict__
