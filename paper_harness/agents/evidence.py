from __future__ import annotations

from .base import Agent, AgentContext, artifact
from ..models import AgentResult


class ClaimAuditor(Agent):
    """Check that draft claims point to known evidence without inventing support."""

    name = "claim-auditor"

    def run(self, context: AgentContext) -> AgentResult:
        drafts = [item for item in context.artifacts if item.kind == "draft"]
        literature = next((item for item in reversed(context.artifacts) if item.kind == "literature_search"), None)
        if not drafts:
            return AgentResult(self.name, "blocked", message="No draft is available for claim auditing.")
        known = set()
        if literature:
            known = {record.get("external_id") or record.get("url") or record.get("title") for record in literature.payload.get("records", [])}
        claims = drafts[-1].payload.get("claims", [])
        audited = []
        for claim in claims:
            source_ids = claim.get("source_ids", [])
            missing = [source_id for source_id in source_ids if source_id not in known]
            audited.append({"claim_id": claim.get("claim_id"), "status": "traceable" if source_ids and not missing else "needs-evidence", "source_ids": source_ids, "missing_source_ids": missing, "semantic_verification": "human-required"})
        unsupported = sum(item["status"] == "needs-evidence" for item in audited)
        return AgentResult(self.name, "completed", [artifact(
            "claim_audit", context.project, self.name,
            {"claims": audited, "unsupported_count": unsupported, "known_source_count": len(known), "human_review_required": True, "note": "Traceability is not proof of semantic support."}, 0.7 if unsupported == 0 else 0.55
        )], "Audited draft claims against the available literature artifacts.")
