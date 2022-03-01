from contextlib import contextmanager

import pytest

from jqtodobackend.models import Todo, TodoChanges, CreatedTodo
from jqtodobackend.db import clear_todos, get_db
from jqtodobackend.backend import app as fastapi_app
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def app():
    try:
        yield fastapi_app
    finally:
        with contextmanager(get_db)() as db:
            clear_todos(db)


@pytest.fixture()
def client(app):
    c = TestClient(app)
    return c


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_to_todos_to_start_with(client):
    response = get_all(client)
    j = response.json()
    assert len(j) == 0


def test_a_posted_todo_is_returned(client):
    todo = Todo(title="a title")
    response = post(client, todo)
    t = response.json()
    assert CreatedTodo.from_dict(t) == CreatedTodo.from_todo(todo)


def test_posted_todos_are_added_to_the_list(client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    post(client, todo_a)
    post(client, todo_b)

    response = get_all(client)

    expected = [CreatedTodo.from_todo(todo_a), CreatedTodo.from_todo(todo_b)]
    assert [CreatedTodo.from_dict(item) for item in response.json()] == expected


def test_list_is_empty_after_deletion(client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    post(client, todo_a)
    post(client, todo_b)
    client.delete("/")

    response = get_all(client)

    expected = []
    assert response.json() == expected


def test_a_todo_is_initially_not_completed(client):
    todo = Todo(title="a title")
    response = post(client, todo)
    assert not response.json()["completed"]


def test_a_created_todo_has_a_url_to_fetch_itself(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))

    response = client.get(url)

    assert CreatedTodo.from_dict(response.json()) == CreatedTodo.from_todo(todo)


def test_a_created_todos_url_is_stored_in_the_list(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))

    response = get_all(client)

    assert [t["url"] for t in response.json()] == [url]


def test_a_todo_can_be_patched_to_change_its_title(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))
    todo_changes = TodoChanges(title="a different title")
    patch(client, url, todo_changes)

    response = client.get(url)

    assert response.json()["title"] == "a different title"


def test_a_todo_can_be_patched_to_change_its_completeness(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))
    todo_changes = TodoChanges(completed=True)
    patch(client, url, todo_changes)

    response = client.get(url)

    assert response.json()["completed"]


def test_changes_to_todos_are_propagated_to_the_list(client):
    todo_a = Todo(title="title a")
    todo_b = Todo(title="title b")
    todo_changes_a = TodoChanges(title="new title a", completed=True)
    todo_changes_b = TodoChanges(completed=True)
    url_a = extract_url(post(client, todo_a))
    url_b = extract_url(post(client, todo_b))
    patch(client, url_a, todo_changes_a)
    patch(client, url_b, todo_changes_b)

    response = get_all(client)

    assert [(t["title"], t["completed"]) for t in response.json()] == [
        ("new title a", True),
        ("title b", True),
    ]


def test_a_todo_can_be_removed_from_the_list_by_deleting_it(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))
    client.delete(url)

    response = get_all(client)

    assert response.json() == []


def test_a_todo_cannot_be_retrieved_after_deleting_it(client):
    todo = Todo(title="a title")
    url = extract_url(post(client, todo))
    client.delete(url)

    response = client.get(url)

    assert response.status_code == 404


def test_a_todo_can_have_an_initial_order(client):
    todo = Todo(title="a title", order=1)
    url = extract_url(post(client, todo))

    response = client.get(url)

    assert response.json()["order"] == 1


def test_a_todo_can_be_patched_to_change_its_order(client):
    todo = Todo(title="a title", order=1)
    url = extract_url(post(client, todo))
    patch(client, url, TodoChanges(order=2))

    response = client.get(url)

    assert response.json()["order"] == 2


def post(client, todo):
    return client.post("/", json=todo.__dict__)


def get_all(client):
    return client.get("/")


def patch(client, url, todo_changes):
    response = client.patch(url, json=todo_changes.__dict__)
    assert response.status_code == 200


def extract_url(response):
    return response.json()["url"]
