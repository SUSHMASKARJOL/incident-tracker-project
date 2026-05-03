"""Logging and retry decorators for service calls."""

import functools
import logging
import time


def log_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Calling %s", func.__name__)
        result = func(*args, **kwargs)
        logging.info("%s completed", func.__name__)
        return result

    return wrapper


def retry(times=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    logging.exception("Attempt %s/%s failed for %s", attempt, times, func.__name__)
                    if attempt == times:
                        raise
                    time.sleep(delay)

        return wrapper

    return decorator

