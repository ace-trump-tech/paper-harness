from .base import DomainPack

HUMANITIES = DomainPack(
    name="humanities",
    evidence_types=["primary_source", "secondary_source", "archive", "interview", "quotation"],
    review_questions=[
        "Are primary and secondary sources clearly separated?",
        "Does the interpretation acknowledge competing theoretical readings?",
        "Can each factual claim be traced to a source and its context?",
    ],
    experiment_modes=["corpus_analysis", "qualitative_coding", "survey"],
    visual_mode="direct",
    visual_constraints=["record historical and cultural references", "separate interpretation from source evidence", "disclose generated imagery"],
)
