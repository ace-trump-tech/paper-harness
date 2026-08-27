from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .base import LiteratureProvider, SourceRecord


class CachedLiteratureProvider(LiteratureProvider):
    """Cache provider responses by normalized query for reproducible reruns."""

    def __init__(self, provider: LiteratureProvider, directory: Path):
        self.provider = provider
        self.name = f"cached-{provider.name}"
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def search(self, query: str, limit: int = 10) -> Iterable[SourceRecord]:
        key = hashlib.sha256(f"{self.provider.name}:{query}:{limit}".encode()).hexdigest()[:20]
        path = self.directory / f"{self.provider.name}-{key}.json"
        if path.exists():
            return [SourceRecord(**item) for item in json.loads(path.read_text(encoding="utf-8"))]
        records = list(self.provider.search(query, limit))
        path.write_text(json.dumps([record.to_dict() for record in records], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return records

