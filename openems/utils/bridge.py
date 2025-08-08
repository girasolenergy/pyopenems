import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable
from asgiref.sync import async_to_sync
import threading

class ASGIRefBridge:
    def __init__(self, max_workers: int = 1) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.isinparentloop = self.isinloop()

        if not self.isinparentloop:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def run(self, async_fn: Callable[..., Any], /, *args, timeout: float | None = None, **kwargs) -> Any:
        if self.isinparentloop:
            fut = self._executor.submit(lambda: async_to_sync(async_fn)(*args, **kwargs))
            return fut.result(timeout=timeout)
        else:
            return self.loop.run_until_complete(async_fn(*args, **kwargs))

    def isinloop(self):
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                return True
            else:
                return False
        except RuntimeError:
            return False

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
