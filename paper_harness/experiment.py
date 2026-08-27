from __future__ import annotations

import subprocess
from dataclasses import asdict
from typing import Any, Dict

from .models import ExperimentSpec


def run_toy_experiment() -> Dict[str, Any]:
    """Run a deterministic, dependency-free experiment for the STEM demo.

    The proposed method is a calibrated threshold on a synthetic score. It is
    intentionally small: the goal is to prove the evidence loop, not to claim
    a scientific result for a real dataset.
    """
    labels = [0, 0, 1, 1, 1, 0, 1, 0]
    scores = [0.12, 0.35, 0.62, 0.91, 0.78, 0.44, 0.57, 0.21]
    baseline_predictions = [int(score >= 0.6) for score in scores]
    proposed_predictions = [int(score >= 0.5) for score in scores]

    def accuracy(predictions):
        return sum(p == y for p, y in zip(predictions, labels)) / len(labels)

    baseline = accuracy(baseline_predictions)
    proposed = accuracy(proposed_predictions)
    return {
        "name": "toy-threshold-evaluation",
        "status": "passed",
        "dataset": {"type": "synthetic", "samples": len(labels), "seed": 7},
        "metrics": {"accuracy": {"baseline": baseline, "proposed": proposed, "delta": proposed - baseline}},
        "limitations": ["synthetic data", "single metric", "not evidence for a real model"],
        "reproducible": True,
    }


class ExperimentRunner:
    """Run reproducible commands; dry-run is the default safety boundary."""

    def run(self, spec: ExperimentSpec) -> Dict[str, Any]:
        if not spec.command or any(not isinstance(part, str) for part in spec.command):
            raise ValueError("experiment command must be a non-empty list of strings")
        if spec.dry_run:
            return {"name": spec.name, "status": "planned", "spec": asdict(spec)}
        try:
            completed = subprocess.run(
                spec.command,
                cwd=spec.cwd,
                capture_output=True,
                text=True,
                timeout=spec.timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {"name": spec.name, "status": "timeout", "stdout": exc.stdout or "", "stderr": exc.stderr or ""}
        return {
            "name": spec.name,
            "status": "passed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
