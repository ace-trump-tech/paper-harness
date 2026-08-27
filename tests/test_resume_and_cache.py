import tempfile
import unittest
from pathlib import Path

from paper_harness.models import Project
from paper_harness.orchestrator import ResearchOrchestrator
from paper_harness.providers.base import LiteratureProvider, SourceRecord
from paper_harness.providers.cache import CachedLiteratureProvider


class FakeProvider(LiteratureProvider):
    name = "fake"

    def __init__(self):
        self.calls = 0

    def search(self, query, limit=10):
        self.calls += 1
        return [SourceRecord(title=query, external_id="fake-1")]


class ResumeAndCacheTest(unittest.TestCase):
    def test_cache_avoids_second_provider_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            provider = FakeProvider()
            cached = CachedLiteratureProvider(provider, Path(tmp))
            self.assertEqual(len(list(cached.search("query"))), 1)
            self.assertEqual(len(list(cached.search("query"))), 1)
            self.assertEqual(provider.calls, 1)

    def test_orchestrator_loads_existing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = Project("resume", objective="test", root=str(root), settings={"execute_toy_experiment": True})
            first = ResearchOrchestrator(root).run_round(project)
            resumed = ResearchOrchestrator(root)
            self.assertEqual(len(resumed.artifacts), len(first["artifacts"]))
            self.assertEqual(resumed.artifacts[0].project_id, project.project_id)

    def test_human_approval_pauses_and_resume_does_not_duplicate_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = Project("approval", objective="test", root=str(root), settings={"require_human_approval": True})
            first = ResearchOrchestrator(root).run_round(project)
            self.assertEqual(first["status"], "approval-required")
            self.assertEqual(first["next_stage"], "adversarial_review")
            project.settings["approved_stages"] = ["adversarial_review", "experiment", "evidence_review", "draft", "final_review"]
            resumed = ResearchOrchestrator(root).run_round(project)
            self.assertEqual(resumed["project"]["stage"], "final_review")
            count = len(resumed["artifacts"])
            done = ResearchOrchestrator(root).run_round(project)
            self.assertEqual(len(done["artifacts"]), count)


if __name__ == "__main__":
    unittest.main()
