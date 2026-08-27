from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DomainPack:
    name: str
    evidence_types: List[str]
    review_questions: List[str]
    experiment_modes: List[str]
    visual_mode: str
    visual_constraints: List[str]

    def critic_prompt(self, hypothesis: str) -> str:
        questions = "\n".join(f"- {item}" for item in self.review_questions)
        return f"Evaluate this hypothesis: {hypothesis}\n{questions}"
