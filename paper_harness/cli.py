from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import Project
from .orchestrator import ResearchOrchestrator


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-harness")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a project from a JSON/YAML-like JSON file")
    init.add_argument("spec")
    init.add_argument("--output", required=True)
    init.add_argument("--edition", choices=["undergraduate", "cv_exploration"], help="select the beginner thesis or CV exploration workflow")
    run = sub.add_parser("run", help="run the deterministic research loop")
    run.add_argument("project")
    run.add_argument("--online", action="store_true", help="enable the configured public literature provider")
    run.add_argument("--no-cache", action="store_true", help="disable the literature response cache")
    approve = sub.add_parser("approve", help="approve a high-risk stage before continuing")
    approve.add_argument("project")
    approve.add_argument("--stage", required=True, choices=["adversarial_review", "experiment", "evidence_review", "draft", "final_review", "all"])
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "init":
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        project = Project(title=spec["title"], domain=spec.get("domain", "stem"), objective=spec.get("objective", ""), root=args.output, settings=spec.get("settings", {}), edition=args.edition or spec.get("edition", "undergraduate"))
        orchestrator = ResearchOrchestrator(Path(args.output))
        orchestrator.save_project(project)
        print(json.dumps(project.to_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "approve":
        project_path = Path(args.project)
        project = Project.from_dict(json.loads(project_path.read_text(encoding="utf-8")))
        approved = list(project.settings.get("approved_stages", []))
        if args.stage not in approved:
            approved.append(args.stage)
        project.settings["approved_stages"] = approved
        project_path.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"approved": args.stage, "project": str(project_path)}, ensure_ascii=False))
        return 0
    project_path = Path(args.project)
    project = Project.from_dict(json.loads(project_path.read_text(encoding="utf-8")))
    if args.online:
        project.settings["online"] = True
    if args.no_cache:
        project.settings["cache"] = False
    result = ResearchOrchestrator(project_path.parent).run_round(project)
    print(json.dumps({"stage": result["project"]["stage"], "artifact_count": len(result["artifacts"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
