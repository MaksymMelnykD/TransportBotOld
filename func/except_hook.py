import traceback
from types import TracebackType

from loguru import logger


def log_uncaught_exceptions(ex_cls, ex, tb: TracebackType):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))
    print(ex)
    logger.trace(text)