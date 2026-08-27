from .integrity import AuthorshipEditor, SimilarityChecker
from .evidence import ClaimAuditor
from .research import AdversarialCritic, EvidenceSynthesizer, ExperimentDesigner, HypothesisGenerator, InnovationGenerator, LiteratureScout
from .writing import DraftWriter
from .visual import CompositionSupervisor, VisualCritic, VisualPlanner
from .profiles import CompositionAgent, CVCombinationAgent, EvaluationSubAgent, GPUSubAgent, KnowledgeBaseAgent, UndergraduateGuideAgent

__all__ = ["AuthorshipEditor", "ClaimAuditor", "CompositionSupervisor", "DraftWriter", "SimilarityChecker", "VisualCritic", "VisualPlanner", "AdversarialCritic", "EvidenceSynthesizer", "ExperimentDesigner", "HypothesisGenerator", "InnovationGenerator", "LiteratureScout", "CompositionAgent", "CVCombinationAgent", "EvaluationSubAgent", "GPUSubAgent", "KnowledgeBaseAgent", "UndergraduateGuideAgent"]
