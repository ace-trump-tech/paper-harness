import unittest

from paper_harness.agents.base import AgentContext, artifact
from paper_harness.agents.integrity import SimilarityChecker
from paper_harness.domain_packs import STEM
from paper_harness.models import Project


class SimilarityLiteratureTest(unittest.TestCase):
    def test_nested_literature_records_are_screened(self):
        project = Project("similarity", objective="test")
        draft = artifact("draft", project, "writer", {"text": "A benchmark measures reliable multimodal evaluation with a calibration protocol.", "claims": []})
        literature = artifact("literature_search", project, "scout", {"records": [{
            "title": "A benchmark measures reliable multimodal evaluation with a calibration protocol",
            "abstract": "",
            "external_id": "source-1",
            "source_kind": "demo",
        }]})
        result = SimilarityChecker().run(AgentContext(project, STEM, [literature, draft]))
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.artifacts[0].payload["matches"][0]["source_id"], "source-1")


if __name__ == "__main__":
    unittest.main()
