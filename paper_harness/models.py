from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Stage(str, Enum):
    BRIEF = "brief"
    LITERATURE = "literature"
    HYPOTHESIS = "hypothesis"
    ADVERSARIAL_REVIEW = "adversarial_review"
    EXPERIMENT = "experiment"
    EVIDENCE_REVIEW = "evidence_review"
    DRAFT = "draft"
    FINAL_REVIEW = "final_review"
    ARCHIVED = "archived"


@dataclass
class Project:
    title: str
    domain: str = "stem"
    objective: str = ""
    project_id: str = field(default_factory=lambda: f"research-{uuid.uuid4().hex[:10]}")
    stage: Stage = Stage.BRIEF
    round: int = 0
    root: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    edition: str = "undergraduate"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["stage"] = self.stage.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        values = dict(data)
        values["stage"] = Stage(values.get("stage", Stage.BRIEF.value))
        return cls(**values)


@dataclass
class Artifact:
    kind: str
    payload: Dict[str, Any]
    project_id: str
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=now_iso)
    agent: str = "system"
    confidence: Optional[float] = None
    sources: List[str] = field(default_factory=list)
    schema_version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentResult:
    agent: str
    status: str
    artifacts: List[Artifact] = field(default_factory=list)
    message: str = ""
    next_actions: List[str] = field(default_factory=list)


@dataclass
class ExperimentSpec:
    name: str
    command: List[str]
    cwd: Optional[str] = None
    timeout_seconds: int = 300
    dry_run: bool = True
