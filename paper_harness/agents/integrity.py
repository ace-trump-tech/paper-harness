from __future__ import annotations

import re
from typing import Iterable, List, Tuple

from .base import Agent, AgentContext, artifact
from ..models import AgentResult


def _tokens(text: str) -> List[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())


def _ngrams(tokens: Iterable[str], size: int = 5) -> set[Tuple[str, ...]]:
    values = list(tokens)
    return {tuple(values[i : i + size]) for i in range(max(0, len(values) - size + 1))}


class SimilarityChecker(Agent):
    """Local overlap screening, not a legal plagiarism verdict."""

    name = "similarity-checker"

    def run(self, context: AgentContext) -> AgentResult:
        drafts = [item for item in context.artifacts if item.kind == "draft"]
        if not drafts:
            return AgentResult(self.name, "blocked", message="No draft artifact is available for similarity screening.")
        draft_ngrams = _ngrams(_tokens(str(drafts[-1].payload.get("text", ""))))
        matches = []
        for source in (item for item in context.artifacts if item.kind in {"source", "literature_record"}):
            source_text = str(source.payload.get("text", source.payload.get("abstract", "")))
            source_ngrams = _ngrams(_tokens(source_text))
            overlap = len(draft_ngrams & source_ngrams) / max(1, len(draft_ngrams))
            if overlap > 0:
                matches.append({"artifact_id": source.artifact_id, "source_id": source.artifact_id, "overlap": round(overlap, 4)})
        literature = [item for item in context.artifacts if item.kind == "literature_search"]
        if literature:
            for record in literature[-1].payload.get("records", []):
                source_text = " ".join([str(record.get("title", "")), str(record.get("abstract", ""))])
                source_ngrams = _ngrams(_tokens(source_text))
                overlap = len(draft_ngrams & source_ngrams) / max(1, len(draft_ngrams))
                if overlap > 0:
                    matches.append({"source_id": record.get("external_id") or record.get("url") or record.get("title"),
                                    "source_kind": record.get("source_kind", "literature"), "overlap": round(overlap, 4)})
        return AgentResult(self.name, "completed", [artifact(
            "similarity_report", context.project, self.name,
            {"method": "normalized-five-gram-screen", "matches": matches, "requires_human_review": True,
             "disclaimer": "This is not a plagiarism determination and cannot replace source-by-source review."}, 0.5
        )], "Screened the draft against locally available source artifacts.")


class AuthorshipEditor(Agent):
    """Improve clarity and author contribution; never evade AI detectors."""

    name = "authorship-editor"

    def run(self, context: AgentContext) -> AgentResult:
        drafts = [item for item in context.artifacts if item.kind == "draft"]
        if not drafts:
            return AgentResult(self.name, "blocked", message="No draft artifact is available for authorship review.")
        text = str(drafts[-1].payload.get("text", ""))
        suggestions = [
            "Replace generic claims with the author's concrete motivation, decisions and limitations.",
            "Attach a source or experiment artifact to every externally verifiable claim.",
            "Keep a revision log and disclose AI assistance according to the target venue's policy.",
        ]
        if len(_tokens(text)) < 80:
            suggestions.append("The draft is too short for a meaningful authorship review; expand the argument first.")
        return AgentResult(self.name, "completed", [artifact(
            "authorship_review", context.project, self.name,
            {"suggestions": suggestions, "provenance_required": True,
             "policy": "Edit for clarity and author ownership; do not optimize for detector evasion."}, 0.65
        )], "Reviewed author contribution, provenance and academic expression.")
