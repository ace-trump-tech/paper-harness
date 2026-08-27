from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional
from dataclasses import asdict


@dataclass
class SourceRecord:
    title: str
    url: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    abstract: str = ""
    source_kind: str = "unknown"
    external_id: str = ""
    venue: str = ""
    cited_by_count: Optional[int] = None

    def to_dict(self):
        return asdict(self)


class LiteratureProvider:
    name = "base"

    def search(self, query: str, limit: int = 10) -> Iterable[SourceRecord]:
        raise NotImplementedError


class TemplateProvider:
    name = "base"

    def find(self, venue: str) -> Iterable[SourceRecord]:
        raise NotImplementedError


class OverleafProvider:
    """Provider boundary; credentials and sync strategy belong to an adapter."""

    name = "overleaf"

    def publish(self, project_dir: str) -> str:
        raise NotImplementedError("configure a local git or approved Overleaf adapter")
