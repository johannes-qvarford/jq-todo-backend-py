from typing import Any
from uuid import UUID

from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, Session, declarative_base

from jqtodobackend.models import CreatedTodo, TodoChanges

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base: Any = declarative_base()


class Todo(Base):
    __tablename__ = "todos"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Boolean)
    order = Column(Integer, nullable=True)

    @property
    def as_created_todo(self):
        d = dict(vars(self))
        d["id"] = UUID(d["id"])
        model = CreatedTodo(**d)
        model.update_url()
        return model


Base.metadata.create_all(bind=engine)


def todos(db: Session) -> list[CreatedTodo]:
    return [todo_schema_to_model(row) for row in db.query(Todo).all()]


def insert_todo(db: Session, todo: CreatedTodo):
    db.add(todo_model_to_schema(todo))
    db.commit()


def remove_todo(db: Session, _id: UUID):
    db.query(Todo).filter_by(id=str(_id)).delete()
    db.commit()


def clear_todos(db: Session):
    db.query(Todo).delete()
    db.commit()


def patch_todo(db: Session, _id: UUID, changes: TodoChanges):
    (
        db.query(Todo)
        .filter_by(id=str(_id))
        .update({k: v for k, v in changes if v is not None})
    )
    db.commit()


def find_todo(db: Session, _id: UUID):
    result = [todo_schema_to_model(x) for x in db.query(Todo).filter_by(id=str(_id))]
    return result[0] if len(result) > 0 else None


def todo_schema_to_model(row: Todo):
    d = dict(vars(row))
    d["id"] = UUID(d["id"])
    model = CreatedTodo(**d)
    model.update_url()
    return model


def todo_model_to_schema(model: CreatedTodo):
    schema = model.dict(exclude={"url"})
    schema["id"] = str(schema["id"])
    return Todo(**schema)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
