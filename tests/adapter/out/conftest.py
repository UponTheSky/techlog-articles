import os
import asyncio

import pytest
import pytest_asyncio
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import AsyncSession

from src.techlog_article.common.database._session import (
    get_current_session,
    set_db_session_context,
    engine,
)
from src.techlog_article.common.database import models


# reference: https://mariogarcia.github.io/blog/2019/10/pytest_fixtures.html

POSTGRES_VERSION = "15.0"


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop

    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_session():
    container = PostgresContainer(f"postgres:{POSTGRES_VERSION}")
    container.start()

    # db setup
    original_db_url = os.environ.get("DB_URL", "")
    os.environ["DB_URL"] = container.get_connection_url()

    # table setup
    # in order to use models.Base.metadata.create_all, we have to use connection
    # instead of the session
    # see the examples in: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
    async with engine.begin() as connection:
        await connection.run_sync(models.Base.metadata.create_all)

    # get the session(setting the context should occur beforehand)
    set_db_session_context(session_id=42)
    current_session = get_current_session()

    yield current_session

    current_session.close()
    os.environ["DB_URL"] = original_db_url
    container.stop()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_up(db_session: AsyncSession):
    for table in reversed(models.Base.metadata.sorted_tables):
        await db_session.execute(table.delete())