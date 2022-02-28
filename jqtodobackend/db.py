from jqtodobackend.models import CreatedTodo

todos_map: list[CreatedTodo] = []


def todos() -> list[CreatedTodo]:
    return todos_map


def find_todo(_id):
    matching_todos = [t for t in todos() if t.id == _id]
    return matching_todos[0] if len(matching_todos) > 0 else None
