# paper-harness

**Languages:** [简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

> A complete research workbench that organizes literature, hypotheses, experiments, code repositories and paper drafts from a research question. It can produce a paper draft and research-code plan, but every claim remains auditable and human-approved.

## Two Editions

| Edition | Repository | Audience | Focus |
| --- | --- | --- | --- |
| General | [paper-harness-undergraduate](https://github.com/ace-trump-tech/paper-harness-undergraduate) | Thesis beginners | Topic decomposition, surveys, bounded experiments, similarity screening and AI-use disclosure |
| Professional | [paper-harness-professional](https://github.com/ace-trump-tech/paper-harness-professional) | Research and engineering teams | Local knowledge, innovation combinations, multi-GPU experiments, metrics, safety and domain demos |

The repositories share resumability, auditability and human approval, while keeping dependencies and workflows independent.

```text
question/codebase -> literature and knowledge base -> innovation candidates
    -> experiments or code tasks -> metrics and failures -> paper draft and repository
    -> claim/license/AI-use review -> human-approved release
```

Run the offline demo in this main repository:

```bash
python3 -m demo.run_demo
open demo/index.html        # macOS
```

The professional edition includes a [power-grid embodied-control demo](https://github.com/ace-trump-tech/paper-harness-professional/tree/main/demo/self-learn) with verified PDFs, extracted text, research cards, experiment protocol and retryable source scripts.

```bash
./scripts/bootstrap-versions.sh
```

This is not an evidence-free black box, an auto-submission tool or an autonomous grid controller. Experiments preserve configuration, seeds, data provenance, metrics, failures and approvals. Numerical solvers, simulators, safety gates and human approval remain authoritative.
