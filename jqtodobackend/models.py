from uuid import UUID, uuid4
from pydantic import BaseModel


class Todo(BaseModel):
    title: str
    order: int | None = None


class CreatedTodo(BaseModel):
    title: str
    id: UUID
    url: str | None = None
    completed: bool = False
    order: int | None = None

    def update_url(self):
        self.url = f"http://localhost:5000/{self.id}"

    @staticmethod
    def from_dict(d):
        no_generated_fields = {k: v for k, v in d.items() if k not in ["url"]}
        return CreatedTodo(**no_generated_fields)

    @staticmethod
    def from_todo(todo):
        created = CreatedTodo(id=uuid4(), **todo.__dict__)
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
