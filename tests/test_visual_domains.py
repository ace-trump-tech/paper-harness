import unittest

from paper_harness.agents.base import AgentContext
from paper_harness.agents.visual import VisualPlanner
from paper_harness.domain_packs import ARTS, STEM
from paper_harness.models import Project


class VisualDomainTest(unittest.TestCase):
    def test_stem_is_modular_and_arts_is_direct(self):
        project = Project("visual demo", objective="explain a pipeline")
        stem = VisualPlanner().run(AgentContext(project, STEM, []))
        arts = VisualPlanner().run(AgentContext(project, ARTS, []))
        self.assertEqual(stem.artifacts[0].payload["mode"], "modular")
        self.assertEqual(arts.artifacts[0].payload["mode"], "direct")
        self.assertGreater(len(stem.artifacts[0].payload["elements"]), 1)


if __name__ == "__main__":
    unittest.main()
