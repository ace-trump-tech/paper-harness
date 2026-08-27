# Architecture

## Principles

- The orchestrator owns state transitions; agents do not mutate project state directly.
- Agent communication uses typed artifacts rather than hidden free-form conversation.
- Every external source and experiment result carries provenance.
- Adversarial critique is a required stage, not an optional reviewer prompt.
- Provider adapters are replaceable and credentials stay outside the repository.
- A rerun loads immutable artifacts and uses query-keyed provider caches; malformed artifacts are rejected before persistence.
- High-risk stages pause until an explicit approval is recorded in the project file; the offline demo may disable this gate for teaching.
- Agent completion is recorded with a stage and reused on resume, so rerunning a project does not duplicate completed work.

## Artifact flow

```text
brief -> literature -> innovation_candidates -> adversarial_search (1..N rounds)
                                      -> experiment_plan -> evidence_review -> draft
                                                                        \-> final_review
```

The CLI exposes the approval boundary explicitly: `paper-harness approve PROJECT --stage experiment`.

## Editions

`undergraduate` and `cv_exploration` use the same `ResearchOrchestrator` as the MainAgent. The MainAgent owns the project state, evidence-chain artifacts, approval gates and recovery behavior; it does not silently make final research decisions.

- `undergraduate` adds a survey-first thesis plan, a bounded teacher-approved experiment template, local similarity screening and AI-use disclosure prompts.
- `cv_exploration` adds a disk-backed, bounded-chunk knowledge base; an A+B+C combination planner; one planned GPU sub-agent per configured device; metric aggregation; and a composition plan for a provenance-aware CV draft.

The current core has no built-in chat UI or uncontrolled training daemon. Human requests are supplied through project configuration and approval events; a chat adapter and external CV runtime can be added as providers without changing the artifact contract.

## Domain-specific visual workflow

The domain pack selects a visual mode. `direct` is suitable for arts and humanities concepts: generate a complete candidate, then apply provenance and author-intent review. `modular` is the default for STEM diagrams and pipelines: plan elements, generate or draw each element, compose them, then check scale, alignment and claim consistency. Both modes end with adversarial visual critique and a human approval gate.

An artifact is immutable in the event log. A revision creates a new artifact and points to its parent through the payload. This supports replay and comparison between competing hypotheses.

## Agent contract

An agent receives a `Project`, a domain pack and prior artifacts. It returns an `AgentResult` containing status, typed artifacts, a human-readable summary and next actions. The initial implementation is deterministic so orchestration tests do not require an LLM or network.

## First vertical slice

The supported STEM demo is intentionally narrow and honest: it imports a small source set, builds a literature matrix, generates three innovation candidates, runs a three-round adversarial search, executes a dependency-free synthetic experiment when explicitly enabled, and writes a Markdown report plus modular SVG pipeline. The synthetic result is a workflow test, not a scientific claim. Similarity screening consumes both standalone source artifacts and records nested in `literature_search`, but remains a local pre-check rather than a plagiarism verdict.

## Extending the system

Implement a provider in `paper_harness.providers`, implement an Agent in `paper_harness.agents`, then register it in an explicit workflow. Do not allow unrestricted agent-to-agent calls; add a transition and an artifact schema first.

## Self-adversarial loop

`SelfAdversarialLoop` keeps multiple candidate hypotheses alive. Each round scores a candidate, attaches attacks, and creates a revised candidate for the next round. The winner is only a ranked research direction; human approval and an actual experiment are still required before it becomes a paper claim.
