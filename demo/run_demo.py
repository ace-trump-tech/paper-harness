#!/usr/bin/env python3
"""Run the offline paper-harness demo and print a research trace."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from paper_harness.models import Project
from paper_harness.orchestrator import ResearchOrchestrator
from paper_harness.report import write_latex_project, write_report, write_stem_pipeline_svg, write_visual_manifest


ROOT = Path(__file__).parent


def main() -> int:
    spec = json.loads((ROOT / "demo_project.json").read_text(encoding="utf-8"))
    project = Project(
        title=spec["title"],
        domain=spec["domain"],
        objective=spec["objective"],
        settings=spec.get("settings", {}),
    )
    output = Path(tempfile.mkdtemp(prefix="paper-harness-demo-"))
    result = ResearchOrchestrator(output).run_round(project)
    artifacts = result["artifacts"]
    write_report(output / "research_report.md", result["project"], artifacts)
    visual = next(item for item in artifacts if item["kind"] == "visual_plan")
    composition = next(item for item in artifacts if item["kind"] == "visual_composition")
    write_stem_pipeline_svg(output / "stem_pipeline.svg", visual["payload"])
    write_visual_manifest(output / "visual_manifest.json", visual["payload"], composition["payload"])
    write_latex_project(output / "latex", result["project"], artifacts)
    print("paper-harness offline demo")
    print("=" * 28)
    print(f"project: {project.title}")
    print(f"artifacts: {len(artifacts)}")
    print(f"output: {output}")
    for item in artifacts:
        print(f"- {item['kind']}")
    search = next(item for item in artifacts if item["kind"] == "adversarial_search")
    print(f"adversarial rounds: {len(search['payload']['rounds'])}")
    print(f"winner: {search['payload']['winner']}")
    print(f"visual mode: {visual['payload']['mode']}")
    experiment = next(item for item in artifacts if item["kind"] == "experiment_result")
    print(f"toy experiment: {experiment['payload']['status']}, accuracy delta={experiment['payload']['metrics']['accuracy']['delta']:.3f}")
    print(f"report: {output / 'research_report.md'}")
    print(f"pipeline svg: {output / 'stem_pipeline.svg'}")
    print(f"visual manifest: {output / 'visual_manifest.json'}")
    print(f"latex project: {output / 'latex' / 'main.tex'}")
    print("Open demo/index.html for the visual summary; you can load the printed run directory there.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
