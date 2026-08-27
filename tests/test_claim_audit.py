import unittest

from paper_harness.agents.base import AgentContext, artifact
from paper_harness.agents.evidence import ClaimAuditor
from paper_harness.domain_packs import STEM
from paper_harness.models import Project


class ClaimAuditTest(unittest.TestCase):
    def test_missing_source_is_not_marked_supported(self):
        project = Project("audit")
        source = artifact("literature_search", project, "test", {"records": [{"external_id": "known"}]})
        draft = artifact("draft", project, "test", {"claims": [{"claim_id": "c1", "text": "claim", "source_ids": ["missing"]}]})
        result = ClaimAuditor().run(AgentContext(project, STEM, [source, draft]))
        self.assertEqual(result.artifacts[0].payload["unsupported_count"], 1)
        self.assertEqual(result.artifacts[0].payload["claims"][0]["status"], "needs-evidence")


if __name__ == "__main__":
    unittest.main()
