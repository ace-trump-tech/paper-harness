from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable
import uuid

from .models import now_iso


class EventLog:
    """Append-only event log used for audit and resume."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, topic: str, payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        event = {
            "event_id": str(uuid.uuid4()),
            "trace_id": trace_id,
            "timestamp": now_iso(),
            "topic": topic,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def read(self) -> Iterable[Dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def last_stage(self, trace_id: str):
        stages = [event["payload"].get("stage") for event in self.read() if event.get("trace_id") == trace_id and event.get("topic") == "stage.changed"]
        return stages[-1] if stages else None
