from typing import Union

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine as create_engine,\
    async_sessionmaker as sessionmaker


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return create_engine(url=url, echo=True)


# создание таблиц в БД
async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    async with engine.begin() as con:
        await con.run_sync(metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
