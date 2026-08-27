from .base import DomainPack

STEM = DomainPack(
    name="stem",
    evidence_types=["paper", "dataset", "code", "experiment", "statistic"],
    review_questions=[
        "Is the hypothesis falsifiable and operationally measurable?",
        "Are baseline, ablation, and evaluation metrics specified?",
        "Could data leakage or confounding explain the result?",
    ],
    experiment_modes=["code", "simulation", "benchmark"],
    visual_mode="modular",
    visual_constraints=["label every element", "preserve coordinate/provenance metadata", "supervise composition against scientific claims"],
)
