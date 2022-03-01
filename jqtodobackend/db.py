from typing import Any
from uuid import UUID

from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from jqtodobackend.models import CreatedTodo

SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base: Any = declarative_base()
# registry = registry()
# Base: Any = registry.generate_base()


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

    @staticmethod
    def from_created_todo(created):
        schema = created.dict(exclude={"url"})
        schema["id"] = str(schema["id"])
        return Todo(**schema)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
