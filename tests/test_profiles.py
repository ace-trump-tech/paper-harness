import tempfile
import unittest
from pathlib import Path

from paper_harness.agents.base import AgentContext
from paper_harness.agents.profiles import CVCombinationAgent, KnowledgeBaseAgent
from paper_harness.domain_packs import STEM
from paper_harness.models import Project
from paper_harness.orchestrator import ResearchOrchestrator
from paper_harness.knowledge import chunk_text


class ProfileTest(unittest.TestCase):
    def test_chunking_bounds_long_text(self):
        chunks = chunk_text("a" * 100, max_chars=30, overlap=5)
        self.assertTrue(all(len(chunk) <= 30 for chunk in chunks))
        self.assertGreater(len(chunks), 3)

    def test_cv_combination_planner_enumerates_ab_combinations(self):
        project = Project("cv", edition="cv_exploration")
        result = CVCombinationAgent().run(AgentContext(project, STEM, []))
        combinations = result.artifacts[0].payload["combinations"]
        self.assertIn("A+B", [item["combination_id"] for item in combinations])
        self.assertIn("A+B+C", [item["combination_id"] for item in combinations])

    def test_knowledge_agent_persists_chunks(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "notes.txt"
            source.write_text("research note " * 30, encoding="utf-8")
            project = Project("kb", root=tmp, settings={"knowledge_files": [str(source)], "knowledge_chunk_chars": 40, "knowledge_chunk_overlap": 5})
            result = KnowledgeBaseAgent().run(AgentContext(project, STEM, []))
            payload = result.artifacts[0].payload
            self.assertEqual(payload["document_count"], 1)
            self.assertTrue((Path(tmp) / "knowledge" / "index.json").exists())

    def test_cv_profile_emits_one_gpu_artifact_per_device(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = Project("cv", edition="cv_exploration", root=str(root), settings={
                "require_human_approval": False,
                "gpu_devices": ["cuda:0", "cuda:1"],
            })
            artifacts = ResearchOrchestrator(root).run_round(project)["artifacts"]
            gpu_runs = [item for item in artifacts if item["kind"] == "gpu_experiment"]
            self.assertEqual({item["payload"]["device"] for item in gpu_runs}, {"cuda:0", "cuda:1"})
            self.assertTrue(all(record["status"] == "planned" for item in gpu_runs for record in item["payload"]["records"]))


if __name__ == "__main__":
    unittest.main()
