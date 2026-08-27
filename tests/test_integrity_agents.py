import unittest

from paper_harness.agents.base import AgentContext, artifact
from paper_harness.agents.integrity import AuthorshipEditor, SimilarityChecker
from paper_harness.domain_packs import STEM
from paper_harness.models import Project


class IntegrityAgentsTest(unittest.TestCase):
    def test_similarity_and_authorship_are_separate_outputs(self):
        project = Project("demo", objective="test objective")
        draft = artifact("draft", project, "test", {"text": "A claim with a source phrase repeated for review."})
        source = artifact("source", project, "test", {"text": "A claim with a source phrase repeated for review."})
        context = AgentContext(project, STEM, [draft, source])
        similarity = SimilarityChecker().run(context)
        authorship = AuthorshipEditor().run(context)
        self.assertEqual(similarity.artifacts[0].kind, "similarity_report")
        self.assertEqual(authorship.artifacts[0].kind, "authorship_review")
        self.assertNotEqual(similarity.agent, authorship.agent)


if __name__ == "__main__":
    unittest.main()

