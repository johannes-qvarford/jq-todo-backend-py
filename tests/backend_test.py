import json

import pytest

import jqtodobackend.backend as backend
from jqtodobackend import Todo
from jqtodobackend import CreatedTodo


@pytest.fixture(autouse=True)
def app():
    app = backend.create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    c = app.test_client()
    return c


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_to_todos_to_start_with(client):
    response = get_all(client)
    j = json.loads(response.data)
    assert len(j) == 0


def test_a_posted_todo_is_returned(client):
    todo = Todo(title="a title")
    response = post(client, todo)
    assert CreatedTodo.from_dict(json.loads(response.data)) == CreatedTodo.from_todo(todo)


def test_posted_todos_are_added_to_the_list(client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    post(client, todo_a)
    post(client, todo_b)

    response = get_all(client)

    expected = [
        CreatedTodo.from_todo(todo_a),
        CreatedTodo.from_todo(todo_b)
    ]
    assert [CreatedTodo.from_dict(item) for item in json.loads(response.data)] == expected


def test_list_is_empty_after_deletion(client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    post(client, todo_a)
    post(client, todo_b)
    client.delete("/")

    response = get_all(client)

    expected = []
    assert json.loads(response.data) == expected


def test_a_todo_is_initially_not_completed(client):
    todo = Todo(title="a title")
    response = post(client, todo)
    assert not json.loads(response.data)['completed']


def test_a_created_todo_has_a_url_to_fetch_itself(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))

    response = client.get(url)

    assert CreatedTodo.from_dict(json.loads(response.data)) == CreatedTodo.from_todo(todo)


def post(client, todo):
    return client.post("/", json=todo.__dict__)


def get_all(client):
    return client.get("/")


def extract_url(response):
    return json.loads(response.data)['url']
