from __future__ import annotations

from typing import Dict, Iterable, List


class SelfAdversarialLoop:
    """Generator/critic loop that revises candidates instead of one-shot scoring."""

    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max(1, min(max_rounds, 8))

    def run(self, candidates: Iterable[Dict], source_records: Iterable[Dict], domain_questions: List[str]) -> Dict:
        current = [dict(candidate) for candidate in candidates]
        sources = list(source_records)
        history = []
        for round_number in range(1, self.max_rounds + 1):
            scored = []
            for candidate in current:
                text = f"{candidate.get('statement', '')} {candidate.get('novelty_claim', '')}".lower()
                overlap = sum(1 for source in sources if any(word in str(source.get('title', '')).lower() for word in text.split() if len(word) > 5))
                attacks = list(domain_questions[:2])
                if overlap:
                    attacks.append("Potential terminology overlap with retrieved work; establish a differentiating contribution.")
                score = max(0.0, round(0.8 - 0.15 * overlap - 0.05 * (round_number - 1), 3))
                scored.append({**candidate, "score": score, "attacks": attacks, "round": round_number})
            scored.sort(key=lambda item: item["score"], reverse=True)
            winner = scored[0] if scored else None
            history.append({"round": round_number, "candidates": scored, "winner": winner.get("candidate_id") if winner else None})
            if round_number < self.max_rounds:
                # Critique feeds the next generator round with a concrete revision request.
                current = [{**item, "statement": item.get("statement", "") + " Address the identified failure modes with a controlled comparison."} for item in scored]
        return {"rounds": history, "winner": history[-1]["winner"] if history else None, "stopping_reason": "max_rounds_reached"}

