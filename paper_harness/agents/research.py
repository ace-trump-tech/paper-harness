from __future__ import annotations

from pathlib import Path
from typing import List

from .base import Agent, AgentContext, artifact
from ..adversarial import SelfAdversarialLoop
from ..models import AgentResult
from ..experiment import run_toy_experiment
from ..providers.base import SourceRecord
from ..providers.public import OpenAlexProvider, PublicApiError
from ..providers.cache import CachedLiteratureProvider


class LiteratureScout(Agent):
    name = "literature-scout"

    def run(self, context: AgentContext) -> AgentResult:
        query = context.project.objective or context.project.title
        settings = context.project.settings
        raw_sources = settings.get("sources", [])
        records = [SourceRecord(**{key: value for key, value in item.items() if key in SourceRecord.__dataclass_fields__}) for item in raw_sources]
        provider_errors = []
        if settings.get("online") and not records:
            try:
                provider = OpenAlexProvider()
                if settings.get("cache", True) and context.project.root:
                    provider = CachedLiteratureProvider(provider, Path(context.project.root) / "cache")
                records.extend(provider.search(query, limit=int(settings.get("literature_limit", 5))))
            except PublicApiError as exc:
                provider_errors.append(str(exc))
        unique = {}
        for record in records:
            key = (record.external_id or record.url or record.title).strip().lower()
            unique[key] = record
        records = list(unique.values())
        matrix = [{
            "source_id": record.external_id or record.url or record.title,
            "title": record.title,
            "year": record.year,
            "venue": record.venue,
            "cited_by_count": record.cited_by_count,
            "relevance": 0.5 if query.lower() in record.title.lower() else 0.25,
            "evidence_status": "abstract_only" if record.abstract else "metadata_only",
        } for record in records]
        status = "completed" if records else "needs-input"
        payload = {
            "query": query,
            "providers": ["arxiv", "openalex", "crossref"],
            "records": [record.to_dict() for record in records],
            "matrix": matrix,
            "required_fields": ["title", "authors", "year", "url", "abstract"],
            "deduplication_key": "doi_or_external_id_or_normalized_title",
            "online_requested": bool(settings.get("online")),
            "provider_errors": provider_errors,
            "next_actions": ["add sources or enable online provider" ] if not records else ["compare candidates against retrieved records"],
        }
        return AgentResult(self.name, status, [artifact("literature_search", context.project, self.name, payload, 0.7 if records else 0.35), artifact("literature_matrix", context.project, self.name, {"rows": matrix, "query": query}, 0.65)],
                           "Retrieved and normalized literature records." if records else "Prepared a search but no source records are available.")


class InnovationGenerator(Agent):
    name = "innovation-generator"

    def run(self, context: AgentContext) -> AgentResult:
        objective = context.project.objective or context.project.title
        candidates = [
            {"candidate_id": "method", "statement": f"Develop a measurable method for {objective}.", "novelty_claim": "Change the method while holding the evaluation protocol constant."},
            {"candidate_id": "data", "statement": f"Improve {objective} through a targeted data or representation intervention.", "novelty_claim": "Change the data/representation bottleneck rather than only the model."},
            {"candidate_id": "evaluation", "statement": f"Re-evaluate {objective} under a failure-aware benchmark.", "novelty_claim": "Expose a limitation that standard aggregate metrics hide."},
        ]
        return AgentResult(self.name, "completed", [artifact(
            "innovation_candidates", context.project, self.name,
            {"candidates": candidates, "evidence_gaps": ["prior-art comparison", "falsifiable metric", "resource estimate"]}, 0.55
        )], "Generated three competing innovation directions with explicit evidence gaps.")


HypothesisGenerator = InnovationGenerator


class AdversarialCritic(Agent):
    name = "adversarial-critic"

    def run(self, context: AgentContext) -> AgentResult:
        candidates = [a for a in context.artifacts if a.kind == "innovation_candidates"]
        if not candidates:
            return AgentResult(self.name, "blocked", message="No innovation candidates are available.")
        literature = next((a for a in reversed(context.artifacts) if a.kind == "literature_search"), None)
        records = literature.payload.get("records", []) if literature else []
        search = SelfAdversarialLoop(max_rounds=int(context.project.settings.get("adversarial_rounds", 3)))
        result = search.run(candidates[-1].payload["candidates"], records, context.domain.review_questions)
        return AgentResult(self.name, "completed", [artifact(
            "adversarial_search", context.project, self.name,
            {"generator": "innovation-generator", "critic": self.name, **result}, 0.7
        )], "Ran a multi-round Generator/Critic loop and ranked the surviving candidates.")


class ExperimentDesigner(Agent):
    name = "experiment-designer"

    def run(self, context: AgentContext) -> AgentResult:
        plan = {"mode": context.domain.experiment_modes[0], "baseline": "fixed threshold", "proposed": "calibrated threshold", "metrics": ["accuracy", "delta"], "dataset": "synthetic toy dataset", "dry_run": not context.project.settings.get("execute_toy_experiment", False)}
        artifacts = [artifact("experiment_plan", context.project, self.name, plan, 0.7)]
        if context.project.settings.get("execute_toy_experiment", False):
            result = run_toy_experiment()
            artifacts.append(artifact("experiment_result", context.project, self.name, result, 0.8))
        return AgentResult(self.name, "completed", artifacts, "Designed the experiment and ran the safe toy experiment." if len(artifacts) > 1 else "Designed an experiment; execution is disabled until explicitly enabled.")


class EvidenceSynthesizer(Agent):
    name = "evidence-synthesizer"

    def run(self, context: AgentContext) -> AgentResult:
        critique_count = sum(a.kind == "adversarial_search" for a in context.artifacts)
        search = next((a for a in reversed(context.artifacts) if a.kind == "adversarial_search"), None)
        experiment = next((a for a in reversed(context.artifacts) if a.kind == "experiment_result"), None)
        return AgentResult(self.name, "completed", [artifact(
            "synthesis", context.project, self.name,
            {"decision": "continue", "reason": "Evidence is incomplete; retain the highest-ranked candidate as a testable direction.", "winner": search.payload.get("winner") if search else None, "experiment_status": experiment.payload.get("status") if experiment else "not-run", "critique_count": critique_count, "human_approval_required": True}, 0.6
        )], "Synthesized current evidence and kept a human approval gate.")
