from __future__ import annotations

from .base import Agent, AgentContext, artifact
from ..models import AgentResult


class DraftWriter(Agent):
    name = "draft-writer"

    def run(self, context: AgentContext) -> AgentResult:
        candidates = [item for item in context.artifacts if item.kind == "innovation_candidates"]
        search = next((item for item in reversed(context.artifacts) if item.kind == "adversarial_search"), None)
        statement = context.project.objective
        if candidates:
            options = candidates[-1].payload.get("candidates", [])
            winner = search.payload.get("winner") if search else None
            selected = next((item for item in options if item.get("candidate_id") == winner), options[0] if options else {})
            statement = selected.get("statement", statement)
        literature = next((item for item in reversed(context.artifacts) if item.kind == "literature_search"), None)
        source_ids = []
        if literature:
            source_ids = [record.get("external_id") or record.get("url") or record.get("title") for record in literature.payload.get("records", [])[:1]]
        text = (
            f"研究目标：{context.project.objective or context.project.title}\n\n"
            f"候选方向：{statement}\n\n"
            "当前证据仍不完整。本草稿只记录可检验的研究主张，不应被视为最终结论。"
        )
        return AgentResult(self.name, "completed", [artifact(
            "draft", context.project, self.name,
            {"format": "plain_text", "text": text, "claims": [{"claim_id": "claim-001", "text": statement, "source_ids": source_ids}], "citations": source_ids, "status": "working_draft"}, 0.5
        )], "Created a provenance-aware working draft, not a submission-ready paper.")
