from __future__ import annotations

from typing import Any, Dict


class SchemaError(ValueError):
    pass


def validate_artifact_payload(kind: str, payload: Dict[str, Any]) -> None:
    required = {
        "literature_search": ["query", "records", "matrix"],
        "literature_matrix": ["rows", "query"],
        "innovation_candidates": ["candidates", "evidence_gaps"],
        "adversarial_search": ["rounds", "winner"],
        "experiment_plan": ["baseline", "proposed", "metrics"],
        "experiment_result": ["status", "metrics", "reproducible"],
        "claim_audit": ["claims", "unsupported_count", "human_review_required"],
        "visual_plan": ["mode", "composition", "supervision", "provider"],
        "visual_composition": ["mode", "output_format", "asset_slots", "provenance", "human_review_required"],
        "knowledge_index": ["root", "documents", "document_count", "chunking", "long_text_policy"],
        "undergraduate_plan": ["mode", "audience", "workflow", "experiment_template", "human_checkpoints"],
        "innovation_combinations": ["components", "combinations", "search_space", "human_selection_required"],
        "gpu_experiment": ["device", "records", "parallelism", "human_approval_required"],
        "cv_evaluation": ["metrics", "sota_comparison", "runs_seen", "recommendations", "human_review_required"],
        "cv_composition": ["inputs", "outputs", "claim_policy", "status", "human_review_required"],
    }.get(kind)
    if required:
        missing = [key for key in required if key not in payload]
        if missing:
            raise SchemaError(f"{kind} artifact missing fields: {', '.join(missing)}")
    if kind == "literature_search" and not isinstance(payload["records"], list):
        raise SchemaError("literature_search.records must be a list")
    if kind == "visual_plan" and payload.get("mode") not in {"direct", "modular"}:
        raise SchemaError("visual_plan.mode must be direct or modular")
    if kind == "visual_composition" and not isinstance(payload["asset_slots"], list):
        raise SchemaError("visual_composition.asset_slots must be a list")
    if kind == "innovation_candidates" and not payload["candidates"]:
        raise SchemaError("innovation_candidates must contain at least one candidate")
    if kind == "experiment_result" and payload["status"] not in {"passed", "failed", "timeout", "planned"}:
        raise SchemaError("unknown experiment result status")
