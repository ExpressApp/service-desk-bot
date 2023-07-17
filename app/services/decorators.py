"""Decorators."""

import asyncio
from functools import partial, wraps
from typing import Any, Callable


def async_wrap(func: Callable) -> Callable:
    """Wrap sync func to async func."""

    @wraps(func)
    async def run(  # noqa: WPS430
        *args: Any, loop: Any = None, executor: Any = None, **kwargs: Any
    ) -> Any:
        if loop is None:
            loop = asyncio.get_event_loop()
        partial_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, partial_func)

    return run
