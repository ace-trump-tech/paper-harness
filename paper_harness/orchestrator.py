from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .agents.base import Agent, AgentContext
from .agents.integrity import AuthorshipEditor, SimilarityChecker
from .agents.evidence import ClaimAuditor
from .agents.research import AdversarialCritic, EvidenceSynthesizer, ExperimentDesigner, InnovationGenerator, LiteratureScout
from .agents.writing import DraftWriter
from .agents.visual import CompositionSupervisor, VisualComposer, VisualCritic, VisualPlanner
from .agents.profiles import CompositionAgent, CVCombinationAgent, EvaluationSubAgent, GPUSubAgent, KnowledgeBaseAgent, UndergraduateGuideAgent
from .domain_packs import PACKS
from .events import EventLog
from .models import Artifact, Project, Stage
from .schemas import validate_artifact_payload
from .state_machine import advance


class ResearchOrchestrator:
    """Small deterministic orchestrator; external runtimes can replace its agents."""

    def __init__(self, project_dir: Path):
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.artifact_dir = self.project_dir / "artifacts"
        self.artifact_dir.mkdir(exist_ok=True)
        self.events = EventLog(self.project_dir / "events.jsonl")
        self.artifacts: List[Artifact] = self._load_artifacts()

    def _load_artifacts(self) -> List[Artifact]:
        loaded = []
        for path in sorted(self.artifact_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                item = Artifact(**data)
                validate_artifact_payload(item.kind, item.payload)
                loaded.append(item)
            except (OSError, ValueError, TypeError):
                continue
        return sorted(loaded, key=lambda item: (item.created_at, item.artifact_id))

    def save_project(self, project: Project) -> None:
        (self.project_dir / "project.json").write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def transition(self, project: Project, target: Stage) -> None:
        project.stage = advance(project.stage, target)
        self.save_project(project)
        self.events.append("stage.changed", {"stage": project.stage.value, "round": project.round}, project.project_id)

    def run_round(self, project: Project) -> Dict[str, object]:
        domain = PACKS.get(project.domain)
        if domain is None:
            raise ValueError(f"unknown domain: {project.domain}; choose one of {sorted(PACKS)}")
        agents: List[Agent] = [KnowledgeBaseAgent(), LiteratureScout(), InnovationGenerator(), AdversarialCritic(), ExperimentDesigner(), EvidenceSynthesizer(), VisualPlanner(), VisualComposer(), DraftWriter(), SimilarityChecker(), AuthorshipEditor(), ClaimAuditor(), VisualCritic(), CompositionSupervisor()]
        if project.edition == "undergraduate":
            agents.insert(3, UndergraduateGuideAgent())
        elif project.edition == "cv_exploration":
            agents.extend([CVCombinationAgent(), EvaluationSubAgent(), CompositionAgent()])
            agents.extend(GPUSubAgent(device) for device in project.settings.get("gpu_devices", ["cuda:0"]))
        elif project.edition != "legacy":
            raise ValueError("unknown edition: choose undergraduate or cv_exploration")
        stages = (Stage.LITERATURE, Stage.HYPOTHESIS, Stage.ADVERSARIAL_REVIEW, Stage.EXPERIMENT, Stage.EVIDENCE_REVIEW, Stage.DRAFT, Stage.FINAL_REVIEW)
        if project.stage == Stage.ARCHIVED:
            return {"project": project.to_dict(), "artifacts": [item.to_dict() for item in self.artifacts]}
        if project.stage == Stage.FINAL_REVIEW and self._stage_completed(project, Stage.FINAL_REVIEW):
            return {"project": project.to_dict(), "artifacts": [item.to_dict() for item in self.artifacts], "status": "complete"}
        project.round += 1
        self.save_project(project)
        start = 0 if project.stage == Stage.BRIEF else max(0, stages.index(project.stage))
        for index, target in enumerate(stages[start:], start=start):
            if self._requires_approval(project, target) and not self._approved(project, target):
                self.events.append("approval.required", {"stage": target.value, "round": project.round}, project.project_id)
                return {"project": project.to_dict(), "artifacts": [item.to_dict() for item in self.artifacts],
                        "status": "approval-required", "next_stage": target.value}
            if project.stage != target:
                self.transition(project, target)
            for agent in (item for item in agents if self._stage_agent(item, target, project)):
                if self._agent_completed(project, target, agent.name):
                    continue
                context = AgentContext(project, domain, list(self.artifacts))
                result = agent.run(context)
                for item in result.artifacts:
                    validate_artifact_payload(item.kind, item.payload)
                    (self.artifact_dir / f"{item.artifact_id}.json").write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                self.artifacts.extend(result.artifacts)
                self.events.append("agent.completed", {"agent": result.agent, "stage": target.value, "status": result.status, "artifact_ids": [a.artifact_id for a in result.artifacts]}, project.project_id)
        self.save_project(project)
        return {"project": project.to_dict(), "artifacts": [item.to_dict() for item in self.artifacts]}

    def _agent_completed(self, project: Project, stage: Stage, agent: str) -> bool:
        return any(event.get("topic") == "agent.completed"
                   and event.get("trace_id") == project.project_id
                   and event.get("payload", {}).get("stage") == stage.value
                   and event.get("payload", {}).get("agent") == agent for event in self.events.read())

    def _stage_completed(self, project: Project, stage: Stage) -> bool:
        expected = {agent.name for agent in (SimilarityChecker(), AuthorshipEditor(), ClaimAuditor(), VisualCritic(), CompositionSupervisor())}
        completed = {event.get("payload", {}).get("agent") for event in self.events.read()
                     if event.get("topic") == "agent.completed" and event.get("trace_id") == project.project_id
                     and event.get("payload", {}).get("stage") == stage.value}
        return expected.issubset(completed)

    @staticmethod
    def _requires_approval(project: Project, stage: Stage) -> bool:
        if not project.settings.get("require_human_approval", True):
            return False
        return stage in {Stage.ADVERSARIAL_REVIEW, Stage.EXPERIMENT, Stage.EVIDENCE_REVIEW, Stage.DRAFT, Stage.FINAL_REVIEW}

    @staticmethod
    def _approved(project: Project, stage: Stage) -> bool:
        approvals = project.settings.get("approved_stages", [])
        return "all" in approvals or stage.value in approvals

    @staticmethod
    def _stage_agent(agent: Agent, stage: Stage, project: Optional[Project] = None) -> bool:
        edition = project.edition if project else "undergraduate"
        mapping = {
            Stage.LITERATURE: {"knowledge-base", "literature-scout"},
            Stage.HYPOTHESIS: {"innovation-generator", "undergraduate-guide"} if edition == "undergraduate" else {"innovation-generator", "cv-combination-planner"},
            Stage.ADVERSARIAL_REVIEW: "adversarial-critic",
            Stage.EXPERIMENT: {"experiment-designer"} if edition != "cv_exploration" else {"experiment-designer"},
            Stage.EVIDENCE_REVIEW: {"evidence-synthesizer"} if edition != "cv_exploration" else {"evidence-synthesizer", "evaluation-subagent"},
            Stage.DRAFT: {"visual-planner", "visual-composer", "draft-writer"} if edition != "cv_exploration" else {"visual-planner", "visual-composer", "draft-writer", "composition-agent"},
        }
        if stage == Stage.FINAL_REVIEW:
            return agent.name in {"similarity-checker", "authorship-editor", "claim-auditor", "visual-critic", "composition-supervisor"}
        if stage == Stage.EXPERIMENT and edition == "cv_exploration" and agent.name.startswith("gpu-subagent["):
            return True
        expected = mapping.get(stage)
        return agent.name in expected if isinstance(expected, set) else expected == agent.name
