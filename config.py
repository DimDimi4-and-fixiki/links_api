import logging
import pathlib

from environs import Env

from common import enums

PROJECT_DIR = pathlib.Path(__file__).parent

env_reader = Env()
env_reader.read_env()

# General app settings
DEFAULT_HOST = '0.0.0.0'
APPLICATION_NAME: str = env_reader.str('APP_NAME', default='API')
VERSION: str = env_reader.str('TAG', default='not_set')
HOST = env_reader.str('HOST', default=DEFAULT_HOST)
PORT = env_reader.int('PORT', default=8089)
DEBUG = env_reader.bool('DEBUG', default=False)
SHUTDOWN_INTERVAL = 2

_old_env_var_value = env_reader.str('ENV', default='local')
_env_var_value = env_reader.str('ENVIRONMENT', default=_old_env_var_value)
ENV: enums.Environment = enums.Environment.from_str(_env_var_value)

# Logging
# One of: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL: str = env_reader.str(
    'LOG_LEVEL',
    default='DEBUG' if ENV.is_local() else 'INFO',
)
logging.basicConfig(level=logging.DEBUG)

# Database
DB_USER = env_reader.str('DB_USER')
DB_HOST = env_reader.str('DB_HOST')
DB_NAME = env_reader.str('DB_NAME')
DB_PASS = env_reader.str('DB_PASS')
DB_PORT = env_reader.int('DB_PORT', default=5432)
DB_CONNECTION_ATTEMPTS = env_reader.int('DB_CONNECTION_ATTEMPTS', default=8)


# Initialise logging
def _bootstrap_loggers() -> None:
    from common.logging import bootstrap_loggers  # circular imports patch

    bootstrap_loggers()


_bootstrap_loggers()

from loguru import logger  # noqa

logger.info(f'Environment is set to - {ENV}')
