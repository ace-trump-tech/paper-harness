import tempfile
import unittest
from pathlib import Path

from paper_harness.agents.base import AgentContext
from paper_harness.agents.visual import VisualComposer, VisualPlanner
from paper_harness.domain_packs import STEM
from paper_harness.models import Project
from paper_harness.report import write_stem_pipeline_svg, write_visual_manifest


class VisualCompositionTest(unittest.TestCase):
    def test_composer_turns_plan_into_auditable_slots(self):
        project = Project("visual demo", objective="explain a pipeline")
        planned = VisualPlanner().run(AgentContext(project, STEM, [])).artifacts
        result = VisualComposer().run(AgentContext(project, STEM, planned))
        payload = result.artifacts[0].payload
        self.assertEqual(payload["output_format"], "svg")
        self.assertEqual([item["id"] for item in payload["asset_slots"]], ["background", "subject", "annotation"])
        self.assertTrue(payload["human_review_required"])

    def test_svg_and_manifest_reflect_the_plan(self):
        plan = {"mode": "modular", "elements": [
            {"id": "background", "purpose": "coordinate frame"},
            {"id": "subject", "purpose": "main phenomenon"},
        ], "composition": {"order": ["background", "subject"]}}
        with tempfile.TemporaryDirectory() as tmp:
            svg = Path(tmp) / "pipeline.svg"
            manifest = Path(tmp) / "visual_manifest.json"
            write_stem_pipeline_svg(svg, plan)
            write_visual_manifest(manifest, plan, {"output_format": "svg"})
            text = svg.read_text(encoding="utf-8")
            self.assertIn("Background", text)
            self.assertIn("Subject", text)
            self.assertIn("HUMAN REVIEW REQUIRED", text)
            self.assertIn('"output_format": "svg"', manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
