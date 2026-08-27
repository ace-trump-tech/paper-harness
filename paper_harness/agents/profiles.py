from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import List

from .base import Agent, AgentContext, artifact
from ..knowledge import LocalKnowledgeBase
from ..models import AgentResult


class KnowledgeBaseAgent(Agent):
    name = "knowledge-base"

    def run(self, context: AgentContext) -> AgentResult:
        root = Path(context.project.root) / "knowledge" if context.project.root else None
        entries = []
        if root:
            entries = LocalKnowledgeBase(root).ingest_files(
                context.project.settings.get("knowledge_files", []),
                max_chars=int(context.project.settings.get("knowledge_chunk_chars", 6000)),
                overlap=int(context.project.settings.get("knowledge_chunk_overlap", 400)),
            )
        payload = {"root": str(root) if root else "memory://knowledge", "documents": entries, "document_count": len(entries), "chunking": {"max_chars": int(context.project.settings.get("knowledge_chunk_chars", 6000)), "overlap": int(context.project.settings.get("knowledge_chunk_overlap", 400))}, "long_text_policy": "store_chunks_on_disk; pass metadata to agents"}
        return AgentResult(self.name, "completed", [artifact("knowledge_index", context.project, self.name, payload, 0.7)], "Indexed local documents into bounded, persistent chunks.")


class UndergraduateGuideAgent(Agent):
    name = "undergraduate-guide"

    def run(self, context: AgentContext) -> AgentResult:
        payload = {"mode": "survey-first", "audience": "undergraduate thesis beginner", "workflow": ["define teacher-provided question", "build a structured review", "choose a feasible baseline", "run a bounded experiment", "check similarity and AI-use disclosure", "write and ask supervisor for confirmation"], "experiment_template": {"baseline": "teacher-approved baseline", "variables": ["one independent variable", "one evaluation metric", "one reproducible configuration"], "stop_rule": "stop when the planned comparison is complete"}, "human_checkpoints": ["scope approval", "source verification", "experiment design approval", "final academic integrity review"]}
        return AgentResult(self.name, "completed", [artifact("undergraduate_plan", context.project, self.name, payload, 0.8)], "Created a survey-first thesis plan with beginner checkpoints.")


class CVCombinationAgent(Agent):
    name = "cv-combination-planner"

    def run(self, context: AgentContext) -> AgentResult:
        components = context.project.settings.get("innovation_components", [
            {"id": "A", "description": "backbone or representation change"},
            {"id": "B", "description": "loss, feature or attention change"},
            {"id": "C", "description": "data, augmentation or evaluation change"},
        ])
        combos = [{"combination_id": "+".join(item[0] for item in group), "components": [item[0] for item in group], "descriptions": [item[1] for item in group], "status": "candidate"} for size in range(1, len(components) + 1) for group in combinations([(item["id"], item["description"]) for item in components], size)]
        return AgentResult(self.name, "completed", [artifact("innovation_combinations", context.project, self.name, {"components": components, "combinations": combos, "search_space": len(combos), "human_selection_required": True}, 0.65)], "Enumerated compositional CV hypotheses for controlled comparison.")


class GPUSubAgent(Agent):
    def __init__(self, device: str):
        self.device = device
        self.name = f"gpu-subagent[{device}]"

    def run(self, context: AgentContext) -> AgentResult:
        combos = next((item.payload.get("combinations", []) for item in reversed(context.artifacts) if item.kind == "innovation_combinations"), [])
        run_enabled = bool(context.project.settings.get("execute_cv_experiments", False))
        records = [{"subagent": self.name, "device": self.device, "combination_id": item.get("combination_id"), "status": "planned" if not run_enabled else "not-configured", "command": context.project.settings.get("cv_command", []), "metrics": {}, "logs": [], "failure": None, "feasibility": "requires-approved-runtime" if not run_enabled else "provider-required"} for item in combos]
        return AgentResult(self.name, "completed", [artifact("gpu_experiment", context.project, self.name, {"device": self.device, "records": records, "parallelism": "one-subagent-per-device", "human_approval_required": True}, 0.55)], f"Prepared {len(records)} CV experiment slots for {self.device}.")


class EvaluationSubAgent(Agent):
    name = "evaluation-subagent"

    def run(self, context: AgentContext) -> AgentResult:
        runs = [item.payload for item in context.artifacts if item.kind == "gpu_experiment"]
        records = [record for payload in runs for record in payload.get("records", [])]
        payload = {"metrics": context.project.settings.get("cv_metrics", ["mAP", "mIoU", "F1", "reconstruction_error"]), "sota_comparison": "requires-imported-reference-results", "runs_seen": len(records), "recommendations": ["compare the same split and protocol", "add ablations for each component", "record failures and resource cost before selecting a winner"], "next_round": "MainAgent may revise A+B+C after human review", "human_review_required": True}
        return AgentResult(self.name, "completed", [artifact("cv_evaluation", context.project, self.name, payload, 0.6)], "Compared available CV run slots and produced the next-round evaluation checklist.")


class CompositionAgent(Agent):
    name = "composition-agent"

    def run(self, context: AgentContext) -> AgentResult:
        payload = {"inputs": [item.kind for item in context.artifacts if item.kind in {"literature_search", "innovation_combinations", "gpu_experiment", "cv_evaluation", "claim_audit"}], "outputs": ["paper_draft", "tables", "figures", "claim_review"], "claim_policy": "every claim must point to literature or experiment artifacts", "status": "working-draft-only", "human_review_required": True}
        return AgentResult(self.name, "completed", [artifact("cv_composition", context.project, self.name, payload, 0.6)], "Prepared a provenance-aware CV paper composition plan.")
