# paper-harness Skill

Use this skill when the user wants a research project decomposed into literature review, hypothesis generation, adversarial critique, experiments, writing, or LaTeX formatting.

## Operating rules

1. Ask for the domain, research objective, constraints, target venue, available data and compute before dispatching work.
2. Create a project brief and keep every claim tied to an artifact or source.
3. Run independent hypothesis generation before selecting one idea.
4. Require an adversarial review before treating an idea as novel or feasible.
5. Require explicit human approval before network searches with credentials, code execution, Overleaf sync, or final submission.
6. Never invent citations. Mark missing evidence as `needs_verification`.
7. Return a concise synthesis to the user, while preserving detailed artifacts and event logs in the project directory.
8. Run `similarity-checker` and `authorship-editor` as separate final-review agents. Similarity screening is not a legal plagiarism verdict; authorship editing must not be used to evade AI detectors.
9. Run at least two Generator/Critic rounds before selecting an innovation candidate. Store every candidate, attack, revision and score as artifacts.
10. Route visual work through the domain pack: use direct generation for arts/humanities concepts; use element planning, composition and supervision for STEM diagrams and pipelines.

## Domain routing

- `stem`: hypotheses, baselines, ablations, metrics, statistical validity and reproducibility.
- `humanities`: source provenance, primary/secondary distinction, interpretive alternatives and quotation context.
- `arts`: concept, medium, process provenance, references, audience feedback and multimodal critique.

## Suggested commands

```bash
python -m paper_harness.cli init examples/stem_project/project.json --output ./artifacts/demo
python -m paper_harness.cli run ./artifacts/demo/project.json
```
