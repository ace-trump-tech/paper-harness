from __future__ import annotations

from .base import Agent, AgentContext, artifact
from ..models import AgentResult


class VisualPlanner(Agent):
    name = "visual-planner"

    def run(self, context: AgentContext) -> AgentResult:
        if context.domain.visual_mode == "direct":
            payload = {
                "mode": "direct",
                "prompt": context.project.objective or context.project.title,
                "composition": "single generation followed by human selection and critique",
                "supervision": ["reference provenance", "author intent", "domain appropriateness"],
                "provider": "image-provider-required",
            }
        else:
            payload = {
                "mode": "modular",
                "elements": [
                    {"id": "background", "purpose": "context and coordinate frame"},
                    {"id": "subject", "purpose": "main object or phenomenon"},
                    {"id": "annotation", "purpose": "labels, arrows or measurement marks"},
                ],
                "composition": {"order": ["background", "subject", "annotation"], "checks": ["scale", "alignment", "claim consistency"]},
                "supervision": context.domain.visual_constraints,
                "provider": "image-provider-required",
            }
        return AgentResult(self.name, "completed", [artifact("visual_plan", context.project, self.name, payload, 0.7)],
                           f"Planned a {context.domain.visual_mode} visual workflow for {context.domain.name}.")


class VisualComposer(Agent):
    """Turn a visual plan into an explicit, provider-agnostic composition spec."""

    name = "visual-composer"

    def run(self, context: AgentContext) -> AgentResult:
        plans = [item for item in context.artifacts if item.kind == "visual_plan"]
        if not plans:
            return AgentResult(self.name, "blocked", message="No visual plan is available.")
        plan = plans[-1].payload
        elements = plan.get("elements", [])
        if plan.get("mode") == "direct":
            slots = [{"id": "canvas", "purpose": "single provider-generated composition"}]
        else:
            slots = [{"id": item["id"], "purpose": item["purpose"]} for item in elements]
        payload = {
            "mode": plan.get("mode"),
            "output_format": "svg",
            "asset_slots": slots,
            "composition": plan.get("composition"),
            "provenance": {"required": True, "provider": plan.get("provider")},
            "human_review_required": True,
            "status": "ready-for-provider-or-editable-export",
        }
        return AgentResult(self.name, "completed", [artifact("visual_composition", context.project, self.name, payload, 0.65)],
                           "Created an auditable composition spec with explicit asset slots and review gates.")


class VisualCritic(Agent):
    name = "visual-critic"

    def run(self, context: AgentContext) -> AgentResult:
        plans = [item for item in context.artifacts if item.kind == "visual_plan"]
        if not plans:
            return AgentResult(self.name, "blocked", message="No visual plan is available.")
        plan = plans[-1].payload
        attacks = [
            "Does the image contain an unsupported claim or visually imply stronger evidence than the paper has?",
            "Can every external reference and generated asset be traced?",
        ]
        if plan.get("mode") == "modular":
            attacks.append("Are element scale, alignment and composition relationships explicitly checked?")
        return AgentResult(self.name, "completed", [artifact("visual_critique", context.project, self.name,
            {"mode": plan.get("mode"), "attacks": attacks, "verdict": "needs-supervision"}, 0.7)],
            "Adversarially reviewed visual claims, provenance and composition.")


class CompositionSupervisor(Agent):
    name = "composition-supervisor"

    def run(self, context: AgentContext) -> AgentResult:
        plans = [item for item in context.artifacts if item.kind == "visual_plan"]
        compositions = [item for item in context.artifacts if item.kind == "visual_composition"]
        if not plans:
            return AgentResult(self.name, "blocked", message="No visual plan is available.")
        mode = plans[-1].payload.get("mode")
        return AgentResult(self.name, "completed", [artifact("composition_review", context.project, self.name,
            {"mode": mode, "status": "human-review-required", "composition_available": bool(compositions),
             "checks": ["provenance", "claim-alignment", "readability", "domain-fit"]}, 0.6)],
            "Created a supervised composition review gate.")
