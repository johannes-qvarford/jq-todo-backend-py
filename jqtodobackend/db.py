import json
from fastapi import Depends

from sqlalchemy import MetaData, Table, create_engine, Column, String, Boolean, Integer
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from jqtodobackend.settings import settings

_metadata = MetaData()
_engine: Engine | None = None

TTodo = Table(
    "todos",
    _metadata,
    Column("id", String, primary_key=True, index=True),
    Column("title", String),
    Column("completed", Boolean),
    Column("order", Integer, nullable=True),
)


def get_engine():
    global _engine, _metadata
    if not _engine:
        _engine = create_engine(
            settings.db_url,
            connect_args=json.loads(settings.db_args),
            echo=True,
            poolclass=StaticPool,
            future=True,
        )
        _metadata.create_all(_engine)
    return _engine


def get_connection(engine: Engine = Depends(get_engine)):
    try:
        with engine.connect() as conn:
            yield conn
    finally:
        if conn is not None:
            conn.close()
