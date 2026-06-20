import logging
import time
from functools import wraps
from typing import Callable, Any
# import newrelic.agent


logger = logging.getLogger(__name__)


def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to log the start and end of a function call,
    including its duration. Automatically sets the New Relic
    background task name to the decorated function's name.

    Args:
        func (Callable): The function being decorated.
    Returns:
        Callable[..., Any]: The decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Set New Relic background task dynamically
        # @newrelic.agent.background_task(name=func.__name__)
        def inner(*i_args: Any, **i_kwargs: Any) -> Any:
            logger.debug(f'Start: {func.__name__}')
            start: float = time.time()
            result: Any = func(*i_args, **i_kwargs)
            end: float = time.time()
            logger.debug(
                f'End: {func.__name__} (Duration: {end - start:.2f}s)'
            )
            return result

        return inner(*args, **kwargs)

    return wrapper
