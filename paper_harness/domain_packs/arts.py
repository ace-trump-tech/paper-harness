from .base import DomainPack

ARTS = DomainPack(
    name="arts",
    evidence_types=["work", "process_log", "reference", "critique", "audience_feedback"],
    review_questions=[
        "Is the concept legible through the selected medium?",
        "Are references, generated assets, and authorship provenance recorded?",
        "Does critique distinguish technical execution from aesthetic judgment?",
    ],
    experiment_modes=["prototype", "user_study", "multimodal_comparison"],
    visual_mode="direct",
    visual_constraints=["preserve artist intent", "record reference and asset provenance", "use critique for composition and medium fit"],
)
