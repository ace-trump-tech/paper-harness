# Offline Demo Report

This report is generated from `demo_project.json` without network access or an API key.

## Research brief

**Goal:** improve the reliability of multimodal model evaluation.

## Literature evidence

The demo imports two source records. A real provider would replace these records with OpenAlex/arXiv/Crossref results while preserving their identifiers and timestamps.

## Competing innovation directions

| Candidate | Direction | Main attack |
| --- | --- | --- |
| method | Change the method while holding evaluation fixed | A baseline may already solve the claimed problem |
| data | Change the data or representation bottleneck | Gains may be caused by data leakage |
| evaluation | Expose failure cases hidden by aggregate metrics | The benchmark may not generalize |

## Self-adversarial search

The Generator proposes the candidates. The Critic attacks novelty, falsifiability and domain constraints. The loop revises candidates for three rounds and returns a ranked winner. The winner is a research direction, not an accepted paper claim.

The toy experiment is deliberately small: the proposed threshold improves the baseline on this synthetic split, but the result is not evidence for a real multimodal model.

## Visual plan

Because this is a STEM task, the visual workflow is modular:

```text
background -> subject -> annotation -> composition review
```

Each element can later be generated or drawn independently, then checked for scale, alignment, provenance and consistency with the paper's claims.
