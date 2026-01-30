import time
import logging
from fastapi import Request
from typing import Iterable, Optional


logger = logging.getLogger(__name__)

def register_middlewares(app, exclude_paths: Optional[Iterable[str]] = None, header_name: str = "X-Process-Time-ms"):
    exclude_set = set(exclude_paths or [])

    def _should_exclude(path: str) -> bool:
        for p in exclude_set:
            if path.startswith(p):
                return True
        return False

    async def measure_time(request: Request, call_next):
        if _should_exclude(request.url.path):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers[header_name] = f"{elapsed_ms:.3f}"
        logger.info("%s %s completed in %.3f ms", request.method, request.url.path, elapsed_ms)
        return response

    app.middleware("http")(measure_time)