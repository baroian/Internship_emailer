from __future__ import annotations

import time
from functools import wraps
from hashlib import sha1
from pathlib import Path
from typing import Callable, Any

from .config import RAW_DIR


def rate_limited(seconds: float) -> Callable:
    def decorator(func: Callable) -> Callable:
        last_called = 0.0

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_called
            elapsed = time.time() - last_called
            if elapsed < seconds:
                time.sleep(seconds - elapsed)
            result = func(*args, **kwargs)
            last_called = time.time()
            return result

        return wrapper

    return decorator


def cache_response(url: str, content: str) -> Path:
    slug = sha1(url.encode()).hexdigest()
    path = RAW_DIR / f"{slug}.html"
    path.write_text(content, encoding="utf-8")
    return path


def load_cached(url: str) -> str | None:
    slug = sha1(url.encode()).hexdigest()
    path = RAW_DIR / f"{slug}.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None
