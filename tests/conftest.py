import asyncio
import inspect
import typing as t
from typing import AsyncIterator
from unittest import mock
from uuid import uuid4

import psycopg2
import pytest
from httpx import AsyncClient
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pytest import FixtureRequest
from tortoise import Model

import config
from commands.run_server import build_app
from core.database import models
from core.database import tools as db_tools


@pytest.fixture(params=['asyncio'], scope='session')
def anyio_backend(request):
    return request.param


@pytest.fixture
def patch_time(mocker):
    def wrap(time: int):
        mocker.patch('time.time', return_value=time)

    return wrap


@pytest.fixture(scope='session')
async def test_app() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=build_app(), base_url='http://testserver') as client:
        yield client


@pytest.fixture(scope='session')
def event_loop() -> t.Iterator[asyncio.AbstractEventLoop]:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # pytest-aiohttp may conflict if not specified
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture(scope='session')
def socket_getfqdn():
    # yoyo.backends.DatabaseBackend.get_log_data
    # Это место очень тормозит при вызове метода getfqdn
    with mock.patch('socket.getfqdn', return_value='') as f:
        yield f


@pytest.fixture(scope='session')
def skip_init_db(request: FixtureRequest):
    for item in request.session.items:
        if 'nodb' not in (marker.name for marker in item.iter_markers()):
            return False
    return True


@pytest.fixture(scope='session', autouse=True)
async def init_db(skip_init_db):
    if skip_init_db:
        yield
        return

    config.DB_NAME = str(uuid4())
    con = psycopg2.connect(
        user=config.DB_USER,
        password=config.DB_PASS,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()

    cursor.execute(f'CREATE DATABASE "{config.DB_NAME}";')

    await db_tools.connect()
    yield

    cursor.execute(
        f'''
        SELECT
            pg_terminate_backend(pid)
        FROM
            pg_stat_activity
        WHERE
            pid <> pg_backend_pid()
            AND datname = '{config.DB_NAME}';
        ''',
    )
    cursor.execute(f'DROP DATABASE IF EXISTS "{config.DB_NAME}";')


@pytest.fixture(autouse=True, scope='session')
async def clean_tables(skip_init_db):
    if skip_init_db:
        yield
        return

    yield

    tables = [
        table for _, table in inspect.getmembers(models, inspect.isclass) if issubclass(table, Model) and table not in (Model,)  # noqa
    ]

    if tables:
        tables = ','.join(
            ['"{}"'.format(table._meta.full_name.lower().split('.')[-1]) for table in tables],  # noqa
        )
        await db_tools.disconnect()
