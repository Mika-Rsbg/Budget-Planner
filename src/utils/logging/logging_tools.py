import logging
import time
from functools import wraps
from typing import Callable, Any


logger = logging.getLogger(__name__)


def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to log the start and end of a function call,
    including its duration.

    Args:
        func (Callable): The function being decorated.
    Returns:
        (Callabel[..., Any]): The decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f'Start: {func.__name__}')
        start: float = time.time()
        result: Any = func(*args, **kwargs)
        end: float = time.time()
        logger.debug(
            f'End: {func.__name__} (Duration: {end - start:.2f}s)'
        )
        return result
    return wrapper
