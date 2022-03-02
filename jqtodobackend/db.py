import json
from uuid import UUID
from os import environ

from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from jqtodobackend.models import CreatedTodo
from jqtodobackend.settings import settings

engine = create_engine(
    settings.db_url,
    connect_args=json.loads(settings.db_args),
    echo=True,
    poolclass=StaticPool,
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
