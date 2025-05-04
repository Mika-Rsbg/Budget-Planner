import logging
import time
from functools import wraps


logger = logging.getLogger(__name__)


def logg(func):
    """
    Decorator to log the start and end of a function call,
    including its duration.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f'Start: {func.__name__}')
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(f'End: {func.__name__} (Duration: {end - start:.2f}s)')
        return result
    return wrapper
