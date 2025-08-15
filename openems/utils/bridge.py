"""ASGI Reference Bridge utilities."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import Callable

from asgiref.sync import async_to_sync


class ASGIRefBridge:
    """Bridge to handle async operations in sync context."""

    def __init__(self, max_workers: int = 1) -> None:
        """Initialize the ASGI Reference Bridge.

        Args:
            max_workers: Maximum number of worker threads.
        """
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.isinparentloop = self.isinloop()

        if not self.isinparentloop:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def run(self, async_fn: Callable[..., Any], /, *args, timeout: float | None = None, **kwargs) -> Any:
        """Run an async function in the appropriate context.

        Args:
            async_fn: The async function to run.
            *args: Positional arguments for the function.
            timeout: Timeout for execution.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the async function.
        """
        if self.isinparentloop:
            fut = self._executor.submit(lambda: async_to_sync(async_fn)(*args, **kwargs))
            return fut.result(timeout=timeout)
        else:
            return self.loop.run_until_complete(async_fn(*args, **kwargs))

    def isinloop(self):
        """Check if currently running in an event loop.

        Returns:
            True if in an active event loop, False otherwise.
        """
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                return True
            else:
                return False
        except RuntimeError:
            return False

    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self._executor.shutdown(wait=True)
