import functools
import importlib
import logging
import os
import string
import sys
import types
import typing

import loguru

import config as cfg

__all__ = ('bootstrap_loggers',)

_logger = loguru.logger

if typing.TYPE_CHECKING:

    class _CustomLoguruRecord(loguru.Record, total=False):  # pragma: no cover
        _serialised: str

else:
    _CustomLoguruRecord = None


def _colorize(line: str, color: str, add_whitespace: bool = True) -> str:
    return f'<{color}>{line}</{color}>{" " if add_whitespace else ""}'


_green = functools.partial(_colorize, color='green')
_red = functools.partial(_colorize, color='red')
_yellow = functools.partial(_colorize, color='yellow')
_blue = functools.partial(_colorize, color='blue')


def _make_plain_formatter() -> typing.Callable[[_CustomLoguruRecord], str]:
    base_log_template = string.Template('{level} $file:{line} {time:YYYY-MM-DD HH:mm:ss,SSS}')
    final_template = base_log_template.substitute(file='{file.path}' if cfg.LOG_LEVEL == 'DEBUG' else '{file}')

    def _format(record: _CustomLoguruRecord) -> str:
        fmt = (
            _green(final_template),
            _yellow('{name}'),
            _blue('{message}', add_whitespace=False),
            os.linesep,
        )

        if record['exception'] is not None:
            fmt += (_red('{exception}', add_whitespace=False), os.linesep)

        return ''.join(fmt)

    return _format


_plain_formatter = _make_plain_formatter()


_loguru_cfg = {
    'handlers': [
        {
            'sink': sys.stdout,
            'format': _plain_formatter,
            'level': cfg.LOG_LEVEL,
            'colorize': cfg.ENV.is_local(),
            'backtrace': False,
            'diagnose': cfg.ENV.is_local(),
        },
    ],
    'activation': [],
}


class InterceptHandler(logging.Handler):  # pragma: no cover
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    logging_libs = (logging.__file__,)

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.startswith('matplotlib'):
            return

        # Get corresponding Loguru level if it exists
        try:
            level: typing.Union[str, int] = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename in self.logging_libs:
            frame = typing.cast(types.FrameType, frame.f_back)
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info,).log(
            level,
            record.getMessage(),
        )


def _bootstrap_lazy_logging_imports() -> None:
    for lib, active in _loguru_cfg['activation']:
        if not (lib and active):
            continue

        try:
            importlib.import_module(lib)
        except ImportError:
            loguru.logger.warning(
                'Cannot eager load logger for library "%s"' % lib,
            )


def bootstrap_loggers() -> None:
    """Setup loguru compatible logging (python logging module)

    * Root handlers are replaced with InterceptHandler
    * All other handlers from any other logging.Logger loggers are erased
    * All logs from logging.Logger goes to root logger -> reroute to loguru

    """
    _bootstrap_lazy_logging_imports()

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(cfg.LOG_LEVEL)

    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    loguru.logger.configure(**_loguru_cfg)
