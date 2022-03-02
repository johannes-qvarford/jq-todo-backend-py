from contextlib import contextmanager

import pytest

from fastapi.testclient import TestClient
from httpx import AsyncClient

from jqtodobackend.backend import app as fastapi_app
from jqtodobackend.db import get_db
from jqtodobackend.models import Todo, TodoChanges, CreatedTodo
from jqtodobackend.repository import TodoRepository


class TodoClient(AsyncClient):
    async def post_async(self, todo):
        return await self.post("/", json=todo.__dict__)

    async def get_all_async(self):
        return await self.get("/")

    async def patch_async(self, url, todo_changes):
        response = await self.patch(url, json=todo_changes.__dict__)
        assert response.status_code == 200


@pytest.fixture(autouse=True)
def app():
    try:
        yield fastapi_app
    finally:
        with contextmanager(get_db)() as db:
            repo = TodoRepository(db)
            repo.clear()


@pytest.fixture()
def client(app):
    c = TestClient(app)
    return c


@pytest.fixture()
def test_client(app):
    return TodoClient(app=app, base_url="http://test")


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.mark.anyio
async def test_to_todos_to_start_with(test_client):
    response = await test_client.get_all_async()
    j = response.json()
    assert len(j) == 0


@pytest.mark.anyio
async def test_a_posted_todo_is_returned(test_client):
    todo = Todo(title="a title")
    response = await test_client.post_async(todo)
    t = response.json()
    assert CreatedTodo.from_dict(t) == CreatedTodo.from_todo(todo)


@pytest.mark.anyio
async def test_posted_todos_are_added_to_the_list(test_client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    await test_client.post_async(todo_a)
    await test_client.post_async(todo_b)

    response = await test_client.get_all_async()

    expected = [CreatedTodo.from_todo(todo_a), CreatedTodo.from_todo(todo_b)]
    assert [CreatedTodo.from_dict(item) for item in response.json()] == expected


@pytest.mark.anyio
async def test_list_is_empty_after_deletion(test_client):
    todo_a = Todo(title="a title")
    todo_b = Todo(title="a different_title")
    await test_client.post_async(todo_a)
    await test_client.post_async(todo_b)
    await test_client.delete("/")

    response = await test_client.get_all_async()

    expected = []
    assert response.json() == expected


@pytest.mark.anyio
async def test_a_todo_is_initially_not_completed(test_client):
    todo = Todo(title="a title")
    response = await test_client.post_async(todo)
    assert not response.json()["completed"]


@pytest.mark.anyio
async def test_a_created_todo_has_a_url_to_fetch_itself(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))

    response = await test_client.get(url)

    assert CreatedTodo.from_dict(response.json()) == CreatedTodo.from_todo(todo)


@pytest.mark.anyio
async def test_a_created_todos_url_is_stored_in_the_list(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))

    response = await test_client.get_all_async()

    assert [t["url"] for t in response.json()] == [url]


@pytest.mark.anyio
async def test_a_todo_can_be_patched_to_change_its_title(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))
    todo_changes = TodoChanges(title="a different title")
    await test_client.patch_async(url, todo_changes)

    response = await test_client.get(url)

    assert response.json()["title"] == "a different title"


@pytest.mark.anyio
async def test_a_todo_can_be_patched_to_change_its_completeness(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))
    todo_changes = TodoChanges(completed=True)
    await test_client.patch_async(url, todo_changes)

    response = await test_client.get(url)

    assert response.json()["completed"]


@pytest.mark.anyio
async def test_changes_to_todos_are_propagated_to_the_list(test_client):
    todo_a = Todo(title="title a")
    todo_b = Todo(title="title b")
    todo_changes_a = TodoChanges(title="new title a", completed=True)
    todo_changes_b = TodoChanges(completed=True)
    url_a = extract_url(await test_client.post_async(todo_a))
    url_b = extract_url(await test_client.post_async(todo_b))
    await test_client.patch_async(url_a, todo_changes_a)
    await test_client.patch_async(url_b, todo_changes_b)

    response = await test_client.get_all_async()

    assert [(t["title"], t["completed"]) for t in response.json()] == [
        ("new title a", True),
        ("title b", True),
    ]


@pytest.mark.anyio
async def test_a_todo_can_be_removed_from_the_list_by_deleting_it(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))
    await test_client.delete(url)

    response = await test_client.get_all_async()

    assert response.json() == []


@pytest.mark.anyio
async def test_a_todo_cannot_be_retrieved_after_deleting_it(test_client):
    todo = Todo(title="a title")
    url = extract_url(await test_client.post_async(todo))
    await test_client.delete(url)

    response = await test_client.get(url)

    assert response.status_code == 404


@pytest.mark.anyio
async def test_a_todo_can_have_an_initial_order(test_client):
    todo = Todo(title="a title", order=1)
    url = extract_url(await test_client.post_async(todo))

    response = await test_client.get(url)

    assert response.json()["order"] == 1


@pytest.mark.anyio
async def test_a_todo_can_be_patched_to_change_its_order(test_client):
    todo = Todo(title="a title", order=1)
    url = extract_url(await test_client.post_async(todo))
    await test_client.patch_async(url, TodoChanges(order=2))

    response = await test_client.get(url)

    assert response.json()["order"] == 2


def extract_url(response):
    return response.json()["url"]
