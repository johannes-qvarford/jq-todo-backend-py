import json
from uuid import UUID
from os import environ

from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from jqtodobackend.models import CreatedTodo

CONNECT_ARGS = (
    environ["DB_ARGS"] if "DB_ARGS" in environ else '{"check_same_thread": false}'
)
SQLALCHEMY_DATABASE_URL = environ["DB_URL"] if "DB_URL" in environ else "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=json.loads(CONNECT_ARGS),
    echo=True,
    poolclass=StaticPool,
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# postgresql://postgres:postgres@db/postgres


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
