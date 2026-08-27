from __future__ import annotations

from typing import Dict, Iterable, Set

from .models import Stage


TRANSITIONS: Dict[Stage, Set[Stage]] = {
    Stage.BRIEF: {Stage.LITERATURE},
    Stage.LITERATURE: {Stage.HYPOTHESIS},
    Stage.HYPOTHESIS: {Stage.ADVERSARIAL_REVIEW},
    Stage.ADVERSARIAL_REVIEW: {Stage.EXPERIMENT, Stage.HYPOTHESIS},
    Stage.EXPERIMENT: {Stage.EVIDENCE_REVIEW, Stage.HYPOTHESIS},
    Stage.EVIDENCE_REVIEW: {Stage.DRAFT, Stage.LITERATURE, Stage.HYPOTHESIS},
    Stage.DRAFT: {Stage.FINAL_REVIEW},
    Stage.FINAL_REVIEW: {Stage.ARCHIVED, Stage.DRAFT, Stage.EXPERIMENT},
    Stage.ARCHIVED: set(),
}


class InvalidTransition(ValueError):
    pass


def can_transition(current: Stage, target: Stage) -> bool:
    return target in TRANSITIONS[current]


def advance(current: Stage, target: Stage) -> Stage:
    if not can_transition(current, target):
        raise InvalidTransition(f"cannot move from {current.value} to {target.value}")
    return target


def allowed_targets(current: Stage) -> Iterable[Stage]:
    return sorted(TRANSITIONS[current], key=lambda item: item.value)

