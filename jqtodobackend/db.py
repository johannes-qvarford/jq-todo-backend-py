import json

from sqlalchemy import MetaData, Table, create_engine, Column, String, Boolean, Integer
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine

from jqtodobackend.settings import settings

engine = create_engine(
    settings.db_url,
    connect_args=json.loads(settings.db_args),
    echo=True,
    poolclass=StaticPool,
    future=True,
)

metadata_obj = MetaData()

TTodo = Table(
    "todos",
    metadata_obj,
    Column("id", String, primary_key=True, index=True),
    Column("title", String),
    Column("completed", Boolean),
    Column("order", Integer, nullable=True),
)

metadata_obj.create_all(engine)


def get_db2():

    try:
        with engine.connect() as conn:
            yield conn
    finally:
        if conn is not None:
            conn.close()
