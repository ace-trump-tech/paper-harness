from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..domain_packs.base import DomainPack
from ..models import AgentResult, Artifact, Project


class AgentContext:
    def __init__(self, project: Project, domain: DomainPack, artifacts: List[Artifact]):
        self.project = project
        self.domain = domain
        self.artifacts = artifacts


class Agent(ABC):
    name = "agent"

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError


def artifact(kind: str, project: Project, agent: str, payload: Dict[str, Any], confidence: float = 0.5) -> Artifact:
    return Artifact(kind=kind, project_id=project.project_id, agent=agent, payload=payload, confidence=confidence)

