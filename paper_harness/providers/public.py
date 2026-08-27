from __future__ import annotations

import json
from urllib.parse import quote
from urllib.request import Request, urlopen
from typing import Iterable

from .base import LiteratureProvider, SourceRecord


class PublicApiError(RuntimeError):
    pass


def _get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "paper-harness/0.1 (+research workflow)"})
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise PublicApiError(f"provider request failed: {exc}") from exc


class OpenAlexProvider(LiteratureProvider):
    name = "openalex"

    def search(self, query: str, limit: int = 10) -> Iterable[SourceRecord]:
        url = "https://api.openalex.org/works?search={}&per-page={}".format(quote(query), min(limit, 50))
        data = _get_json(url)
        for item in data.get("results", []):
            yield SourceRecord(
                title=item.get("title", ""),
                url=item.get("doi") or item.get("id", ""),
                authors=[a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])],
                year=item.get("publication_year"),
                abstract="",
                source_kind=self.name,
                external_id=item.get("id", ""),
                venue=(item.get("primary_location") or {}).get("source", {}).get("display_name", "") if item.get("primary_location") else "",
                cited_by_count=item.get("cited_by_count"),
            )


class ArxivProvider(LiteratureProvider):
    name = "arxiv"

    def search(self, query: str, limit: int = 10) -> Iterable[SourceRecord]:
        # The Atom response is intentionally left to a later adapter; using
        # OpenAlex first keeps the initial provider dependency-free and typed.
        raise PublicApiError("arXiv adapter is not enabled yet; import an Atom adapter explicitly")
