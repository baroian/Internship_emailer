from __future__ import annotations

import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin

from .utils import cache_response, load_cached, rate_limited


@rate_limited(1.0)
def _fetch(url: str) -> str:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return True


def fetch_people_page(url: str) -> str:
    cached = load_cached(url)
    if cached:
        return cached
    if not allowed(url):
        raise PermissionError(f"Robots.txt disallows {url}")
    html = _fetch(url)
    cache_response(url, html)
    return html
