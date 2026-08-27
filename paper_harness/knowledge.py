"""Small local knowledge-base primitives with bounded text chunks.

The module deliberately stores chunks on disk and only passes metadata through
Agent artifacts. This keeps long PDFs out of prompts and makes later retrieval
deterministic without requiring a vector database.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def chunk_text(text: str, max_chars: int = 6000, overlap: int = 400) -> List[str]:
    if max_chars <= 0 or overlap < 0 or overlap >= max_chars:
        raise ValueError("overlap must be non-negative and smaller than max_chars")
    normalized = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + max_chars)
        chunks.append(normalized[start:end])
        if end == len(normalized):
            break
        start = end - overlap
    return chunks


class LocalKnowledgeBase:
    """Persist bounded chunks and a compact index for local research notes."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.chunk_dir = self.root / "chunks"
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"

    def ingest_text(self, text: str, source: str, max_chars: int = 6000, overlap: int = 400) -> Dict[str, object]:
        chunks = chunk_text(text, max_chars=max_chars, overlap=overlap)
        source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chunk_ids = []
        for number, chunk in enumerate(chunks):
            chunk_id = hashlib.sha256(f"{source_hash}:{number}".encode()).hexdigest()[:20]
            (self.chunk_dir / f"{chunk_id}.json").write_text(json.dumps({"chunk_id": chunk_id, "source": source, "number": number, "text": chunk}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            chunk_ids.append(chunk_id)
        entry = {"source": source, "sha256": source_hash, "chunk_ids": chunk_ids, "chunk_count": len(chunk_ids)}
        index = self._read_index()
        index = [item for item in index if item.get("source") != source]
        index.append(entry)
        self.index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return entry

    def ingest_files(self, paths: Iterable[str], max_chars: int = 6000, overlap: int = 400) -> List[Dict[str, object]]:
        entries = []
        for raw_path in paths:
            path = Path(raw_path)
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            entries.append(self.ingest_text(text, str(path), max_chars=max_chars, overlap=overlap))
        return entries

    def _read_index(self) -> List[Dict[str, object]]:
        if not self.index_path.exists():
            return []
        try:
            value = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        return value if isinstance(value, list) else []
