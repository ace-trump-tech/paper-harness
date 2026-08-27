# Evaluation plan

The harness should be evaluated as a research workflow, not only as a text generator.

## Initial metrics

- **Citation precision**: fraction of cited claims supported by the cited source.
- **Citation recall**: relevant sources retrieved for a predefined benchmark query.
- **Novelty precision**: fraction of proposed gaps that survive expert review.
- **Feasibility rate**: fraction of selected ideas that produce a valid experiment plan and result.
- **Adversarial value**: number of material issues found before final review.
- **Reproducibility**: ability to replay artifacts and rerun an experiment from a clean environment.
- **Cost and latency**: model calls, network calls, execution time and human approval count.

## Benchmark shape

Each benchmark task should include a research brief, a frozen source set, known baselines, expected failure modes and an expert-reviewed answer key. Network-dependent runs must record provider, timestamp and query so that later comparisons remain meaningful.

