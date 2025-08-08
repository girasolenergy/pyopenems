import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable
from asgiref.sync import async_to_sync

class ASGIRefBridge:
    def __init__(self, max_workers: int = 1) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def run(self, async_fn: Callable[..., Any], /, *args, timeout: float | None = None, **kwargs) -> Any:
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                fut = self._executor.submit(lambda: async_to_sync(async_fn)(*args, **kwargs))
                return fut.result(timeout=timeout)
        except RuntimeError:
            pass
        return async_to_sync(async_fn)(*args, **kwargs)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
