from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable, Mapping, Optional


def write_stem_pipeline_svg(path: Path, visual_plan: Optional[Mapping] = None) -> None:
    """Write an editable SVG from a visual plan (keeps a useful default for callers)."""
    plan = dict(visual_plan or {})
    mode = plan.get("mode", "modular")
    raw_elements = plan.get("elements") or [
        {"id": "background", "purpose": "context and coordinate frame"},
        {"id": "subject", "purpose": "main object or phenomenon"},
        {"id": "annotation", "purpose": "labels, arrows or measurement marks"},
    ]
    elements = [{"id": str(item.get("id", "element")), "purpose": str(item.get("purpose", "asset slot"))} for item in raw_elements]
    if mode == "direct":
        elements = [{"id": "canvas", "purpose": "single provider-generated composition"}]
    composition = plan.get("composition")
    order = composition.get("order") if isinstance(composition, Mapping) else None
    order = order or [item["id"] for item in elements]
    by_id = {item["id"]: item for item in elements}
    ordered = [by_id[item] for item in order if item in by_id]
    ordered += [item for item in elements if item not in ordered]
    width = max(720, 230 * len(ordered) + 80)
    box_width = min(210, max(150, (width - 80 - 28 * (len(ordered) - 1)) // max(1, len(ordered))))
    y, box_height = 92, 92
    colors = ["#2f6fed", "#167c68", "#c46a22", "#7148a6", "#58677a"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="250" viewBox="0 0 {width} 250">',
             '<style>text{font-family:Arial,sans-serif;fill:#17202b}.box{fill:#fff;stroke-width:2}.arrow{stroke:#8793a1;stroke-width:2;marker-end:url(#arrow)}.small{fill:#5d6978}</style>',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#8793a1"/></marker></defs>',
             f'<rect width="{width}" height="250" rx="14" fill="#f6f8fb"/>',
             f'<text x="34" y="38" font-size="23" font-weight="bold">{html.escape("STEM modular visual workflow" if mode == "modular" else "Direct visual workflow")}</text>',
             '<text x="34" y="63" class="small" font-size="13">Plan assets independently, compose explicitly, then review claims and provenance.</text>']
    x_positions = []
    for index, item in enumerate(ordered):
        x = 40 + index * (box_width + 28)
        x_positions.append(x)
        color = colors[index % len(colors)]
        label = item["id"].replace("_", " ").title()
        purpose = item["purpose"]
        parts.extend([f'<rect class="box" x="{x}" y="{y}" width="{box_width}" height="{box_height}" rx="10" stroke="{color}"/>',
                      f'<circle cx="{x + 22}" cy="{y + 25}" r="9" fill="{color}"/>',
                      f'<text x="{x + 40}" y="{y + 31}" font-size="17" font-weight="bold">{html.escape(label)}</text>',
                      f'<text x="{x + 18}" y="{y + 60}" class="small" font-size="12">{html.escape(purpose[:34])}</text>'])
    for left, right in zip(x_positions, x_positions[1:]):
        parts.append(f'<path class="arrow" d="M{left + box_width} {y + 46} H{right - 8}"/>')
    review_x = width - 205
    parts.extend([f'<rect x="{review_x}" y="205" width="165" height="28" rx="14" fill="#17202b"/>',
                  f'<text x="{review_x + 20}" y="224" font-size="12" fill="#fff" style="fill:#fff">HUMAN REVIEW REQUIRED</text>', '</svg>'])
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_visual_manifest(path: Path, visual_plan: Mapping, visual_composition: Optional[Mapping] = None) -> None:
    """Persist the visual plan and composition metadata next to generated assets."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"visual_plan": dict(visual_plan), "visual_composition": dict(visual_composition or {}),
               "pixel_generation": "provider-not-configured", "human_review_required": True}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_report(path: Path, project: Mapping, artifacts: Iterable[Mapping]) -> None:
    items = list(artifacts)
    by_kind = {item["kind"]: item["payload"] for item in items}
    winner = by_kind.get("adversarial_search", {}).get("winner", "pending")
    experiment = by_kind.get("experiment_result", {})
    records = by_kind.get("literature_search", {}).get("records", [])
    audit = by_kind.get("claim_audit", {})
    lines = [
        f"# {project['title']}", "", "## Evidence-backed STEM demo", "",
        f"Objective: {project.get('objective', '')}", "",
        f"Literature records: {len(records)}", f"Adversarial winner: `{winner}`", "",
        "## Experiment result", "",
        json.dumps(experiment or {"status": "not-run"}, ensure_ascii=False, indent=2), "",
        "## Claim audit", "",
        f"Traceable claims: {sum(item.get('status') == 'traceable' for item in audit.get('claims', []))}",
        f"Claims needing evidence: {audit.get('unsupported_count', 'not-run')}",
        "Traceability is not semantic proof; human review remains required.", "",
        "## Reproducibility", "",
        "This report is a toy experiment artifact. It is not evidence that the proposed method works on a real dataset.", "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _latex_escape(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in value)


def write_latex_project(directory: Path, project: Mapping, artifacts: Iterable[Mapping]) -> Path:
    """Export a minimal, local LaTeX project with explicit evidence limits."""
    directory.mkdir(parents=True, exist_ok=True)
    items = list(artifacts)
    by_kind = {item["kind"]: item["payload"] for item in items}
    title = _latex_escape(str(project.get("title", "Research project")))
    objective = _latex_escape(str(project.get("objective", "")))
    winner = _latex_escape(str(by_kind.get("adversarial_search", {}).get("winner", "pending")))
    experiment = by_kind.get("experiment_result", {})
    delta = experiment.get("metrics", {}).get("accuracy", {}).get("delta", "not-run")
    records = by_kind.get("literature_search", {}).get("records", [])
    citation = "" if not records else " See the imported source records in the bibliography."
    tex = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{booktabs}
\usepackage{url}
\title{%s}
\author{paper-harness working draft}
\date{\today}
\begin{document}
\maketitle
\section{Research brief}
%s
\section{Candidate direction}
The current adversarially ranked direction is \texttt{%s}. This is a research direction, not an accepted novelty claim.%s
\section{Experiment}
The local toy experiment reports an accuracy delta of \texttt{%s}. It uses synthetic data and is included only to validate the workflow.
\section{Evidence and limitations}
All citations and claims must be checked against the generated claim audit before submission. The current draft is not submission-ready and does not establish a result on a real dataset.
\bibliographystyle{plain}
\bibliography{references}
\end{document}
""" % (title, objective, winner, citation, _latex_escape(str(delta)))
    path = directory / "main.tex"
    path.write_text(tex, encoding="utf-8")
    bib_lines = []
    for index, record in enumerate(records, 1):
        key = f"source{index}"
        authors = " and ".join(record.get("authors") or ["Unknown"])
        bib_lines.extend([
            f"@misc{{{key},",
            f"  title = {{{_latex_escape(str(record.get('title', 'Untitled')))}}},",
            f"  author = {{{_latex_escape(authors)}}},",
            f"  year = {{{record.get('year') or 'n.d.'}}},",
            f"  howpublished = {{\\url{{{record.get('url', '')}}}}}",
            "}\n",
        ])
    (directory / "references.bib").write_text("\n".join(bib_lines), encoding="utf-8")
    return path
