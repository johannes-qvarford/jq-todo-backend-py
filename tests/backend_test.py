from contextlib import contextmanager
from typing import Any, List
from fastapi import FastAPI

import pytest

from fastapi.testclient import TestClient

from jqtodobackend.backend import app as fastapi_app
from jqtodobackend.db import get_db2
from jqtodobackend.models import Todo, TodoChanges, CreatedTodo
from jqtodobackend.repository import TodoRepository


class TodoClient:
    def __init__(self, app: FastAPI):
        self._client = TestClient(app)
        pass

    def post(self, todo):
        return self._client.post("/", json=todo.__dict__)

    def get_all(self):
        return self._client.get("/")

    def patch(self, url, todo_changes):
        response = self._client.patch(url, json=todo_changes.__dict__)
        assert response.status_code == 200

    def delete(self, url):
        return self._client.delete(url)

    def get(self, url):
        return self._client.get(url)


@pytest.fixture(autouse=True)
def app():
    try:
        yield fastapi_app
    finally:
        with contextmanager(get_db2)() as db2:
            repo = TodoRepository(db2)
            repo.clear()


@pytest.fixture()
def client(app):
    c = TestClient(app)
    return c


@pytest.fixture()
def test_client(app):
    return TodoClient(app=app)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_to_todos_to_start_with(test_client: TodoClient):
    response = test_client.get_all()
    j = response.json()
    assert len(j) == 0


def test_a_posted_todo_is_returned(test_client: TodoClient):
    todo = Todo(title="a title")
    response = test_client.post(todo)
    t = response.json()
    assert CreatedTodo.from_dict(t) == CreatedTodo.from_todo(todo)


def test_posted_todos_are_added_to_the_list(test_client: TodoClient):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    test_client.post(todo_a)
    test_client.post(todo_b)

    response = test_client.get_all()

    expected = [CreatedTodo.from_todo(todo_a), CreatedTodo.from_todo(todo_b)]
    assert [CreatedTodo.from_dict(item) for item in response.json()] == expected


def test_list_is_empty_after_deletion(test_client: TodoClient):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    test_client.post(todo_a)
    test_client.post(todo_b)
    test_client.delete("/")

    response = test_client.get_all()

    expected: List[dict[str, Any]] = []
    assert response.json() == expected


def test_a_todo_is_initially_not_completed(test_client: TodoClient):
    todo = Todo(title="a title")
    response = test_client.post(todo)
    assert not response.json()["completed"]


def test_a_created_todo_has_a_url_to_fetch_itself(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))

    response = test_client.get(url)

    assert CreatedTodo.from_dict(response.json()) == CreatedTodo.from_todo(todo)


def test_a_created_todos_url_is_stored_in_the_list(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))

    response = test_client.get_all()

    assert [t["url"] for t in response.json()] == [url]


def test_a_todo_can_be_patched_to_change_its_title(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))
    todo_changes = TodoChanges(title="a different title")
    test_client.patch(url, todo_changes)

    response = test_client.get(url)

    assert response.json()["title"] == "a different title"


def test_a_todo_can_be_patched_to_change_its_completeness(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))
    todo_changes = TodoChanges(completed=True)
    test_client.patch(url, todo_changes)

    response = test_client.get(url)

    assert response.json()["completed"]


def test_changes_to_todos_are_propagated_to_the_list(test_client: TodoClient):
    todo_a = Todo(title="title a")
    todo_b = Todo(title="title b")
    todo_changes_a = TodoChanges(title="new title a", completed=True)
    todo_changes_b = TodoChanges(completed=True)
    url_a = extract_url(test_client.post(todo_a))
    url_b = extract_url(test_client.post(todo_b))
    test_client.patch(url_a, todo_changes_a)
    test_client.patch(url_b, todo_changes_b)

    response = test_client.get_all()

    assert [(t["title"], t["completed"]) for t in response.json()] == [
        ("new title a", True),
        ("title b", True),
    ]


def test_a_todo_can_be_removed_from_the_list_by_deleting_it(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))
    test_client.delete(url)

    response = test_client.get_all()

    assert response.json() == []


def test_a_todo_cannot_be_retrieved_after_deleting_it(test_client: TodoClient):
    todo = Todo(title="a title")
    url = extract_url(test_client.post(todo))
    test_client.delete(url)

    response = test_client.get(url)

    assert response.status_code == 404


def test_a_todo_can_have_an_initial_order(test_client: TodoClient):
    todo = Todo(title="a title", order=1)
    url = extract_url(test_client.post(todo))

    response = test_client.get(url)

    assert response.json()["order"] == 1


def test_a_todo_can_be_patched_to_change_its_order(test_client: TodoClient):
    todo = Todo(title="a title", order=1)
    url = extract_url(test_client.post(todo))
    test_client.patch(url, TodoChanges(order=2))

    response = test_client.get(url)

    assert response.json()["order"] == 2


def extract_url(response):
    return response.json()["url"]
