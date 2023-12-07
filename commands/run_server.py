import asyncio
import logging

import config
from app import build_app
from core.database import tools as db_tools

log = logging.getLogger('server')


def main_app(*args, **kwargs):
    app = build_app()

    @app.on_event('startup')
    async def startup():
        log.info('Init DB connection')
        await db_tools.connect()

    @app.on_event('shutdown')
    async def shutdown():
        log.info('Shutdown service and DB connection')
        await asyncio.sleep(config.SHUTDOWN_INTERVAL)
        await db_tools.disconnect()

    return app
