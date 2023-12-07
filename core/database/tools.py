import logging
import pathlib
import time

import psycopg2
import yoyo
from tortoise import Tortoise
from tortoise.backends.base.client import BaseDBAsyncClient

import config

logger = logging.getLogger('db_logger')


__all__ = ['get_connection', 'is_available_connection', 'connect', 'disconnect']


def get_db_dns(with_params: bool = False) -> str:
    url = f'postgres://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}'

    if with_params:
        url += '?maxsize=10' + '&minsize=4'

    return url


def apply_migrations() -> None:
    """
    Применение миграций к БД
    """

    logger.info('Apply migrations')
    backend = yoyo.get_backend(get_db_dns())

    with backend.lock():
        migrations = yoyo.read_migrations(
            (pathlib.Path(__file__).parent / 'migrations').as_posix(),
        )

        if not migrations:
            logger.info('No migrations to apply')
            return

        backend.apply_migrations(backend.to_apply(migrations))


async def connect(connection_attempts: None | int = None) -> None:
    """
    Подключение к БД
    """

    logger.info('Initializing a database connection')

    await Tortoise.init(
        db_url=get_db_dns(with_params=True),
        modules={'models': ['core.database.models']},
    )

    connection_attempts = connection_attempts or config.DB_CONNECTION_ATTEMPTS

    for idx in range(connection_attempts):

        try:
            apply_migrations()
        except psycopg2.OperationalError:
            if idx == connection_attempts - 1:
                raise

            logger.info('DB unavailable')
            time.sleep(1)
            continue

        else:
            break


async def disconnect() -> None:
    """
    Отключение от БД.
    Если приложение исполняется в тестах, то не делаем отключение от БД, т.к. это не оптимально
    """

    await Tortoise.close_connections()


def get_connection() -> BaseDBAsyncClient:
    """
    Получение текущего подключения к бд в потоке
    """
    return Tortoise.get_connection('default')


async def is_available_connection() -> bool:
    """
    Проверка активности текущего подключения к БД
    """

    try:
        return (await get_connection().execute_query('select 1;'))[0] == 1
    except Exception:  # noqa
        return False
