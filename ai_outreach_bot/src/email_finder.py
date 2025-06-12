from __future__ import annotations

import re
from typing import Dict

import requests

from .config import EMAIL_FINDER_API_KEY

# full email regex
EMAIL_REGEX = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def from_page(html: str, domain: str) -> str | None:
    for match in EMAIL_REGEX.findall(html):
        if match.endswith(domain):
            return match
    return None


def from_api(name: str, domain: str) -> str | None:
    if not EMAIL_FINDER_API_KEY:
        return None
    url = "https://api.hunter.io/v2/email-finder"
    params = {"domain": domain, "full_name": name, "api_key": EMAIL_FINDER_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("email")
    except Exception:
        return None


def guess_pattern(name: str, domain: str) -> str:
    parts = name.lower().split()
    first, last = parts[0], parts[-1]
    return f"{first}.{last}@{domain}"


def find_email(name: str, domain: str, html: str | None = None) -> Dict:
    if html:
        email = from_page(html, domain)
        if email:
            return {"email": email, "method": "page", "confidence": 0.9}
    email = from_api(name, domain)
    if email:
        return {"email": email, "method": "api", "confidence": 0.8}
    email = guess_pattern(name, domain)
    return {"email": email, "method": "guess", "confidence": 0.5}
