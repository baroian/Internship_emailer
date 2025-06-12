from __future__ import annotations

import time
from typing import List

import requests

BASE_ARXIV = "http://export.arxiv.org/api/query"
BASE_OPENALEX = "https://api.openalex.org/works"


def _backoff_get(url: str, params: dict) -> requests.Response:
    delay = 1.0
    while True:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 429:
            resp.raise_for_status()
            return resp
        time.sleep(delay)
        delay = min(delay * 2, 60)


def query_arxiv(lab_name: str, max_hits: int = 25) -> List[dict]:
    params = {"search_query": f"all:{lab_name}", "start": 0, "max_results": max_hits}
    resp = _backoff_get(BASE_ARXIV, params)
    entries = []
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text, "xml")
    for entry in soup.find_all("entry"):
        title = entry.title.text.strip()
        authors = [a.find("name").text for a in entry.find_all("author")]
        year = entry.published.text[:4]
        url = entry.id.text
        entries.append({"title": title, "authors": authors, "year": year, "url": url})
    return entries


def query_openalex(lab_name: str, max_hits: int = 25) -> List[dict]:
    params = {"search": lab_name, "per-page": max_hits}
    resp = _backoff_get(BASE_OPENALEX, params)
    data = resp.json()
    results = []
    for item in data.get("results", []):
        title = item.get("title")
        authors = [
            a.get("author", {}).get("display_name") for a in item.get("authorships", [])
        ]
        year = item.get("publication_year")
        url = item.get("id")
        results.append({"title": title, "authors": authors, "year": year, "url": url})
    return results
