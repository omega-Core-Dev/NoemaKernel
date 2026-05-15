"""Context reactivation and cognitive reconstruction metrics."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .bankmap import Anchor, BankmapEngine, ContextItem, InferencePacket


@dataclass(slots=True)
class ReactivationResult:
    context_id: str
    anchor_count: int
    original_terms: int
    reactivated_terms: int
    reactivation_ratio: float
    reconstruction_ratio: float
    cognitive_reconstruction_score: float
    missing_terms: list[str]

    def to_dict(self) -> dict:
        return {
            "context_id": self.context_id,
            "anchor_count": self.anchor_count,
            "original_terms": self.original_terms,
            "reactivated_terms": self.reactivated_terms,
            "reactivation_ratio": self.reactivation_ratio,
            "reconstruction_ratio": self.reconstruction_ratio,
            "cognitive_reconstruction_score": self.cognitive_reconstruction_score,
            "missing_terms": self.missing_terms[:12],
        }


class ReactivationEvaluator:
    """Evaluate whether selected anchors can reactivate original contexts."""

    def __init__(self) -> None:
        self.engine = BankmapEngine()

    def evaluate(self, contexts: list[ContextItem], packet: InferencePacket) -> dict:
        by_context = self._anchors_by_context(packet.anchors)
        results = [
            self._evaluate_context(context, by_context.get(context.context_id, []))
            for context in contexts
        ]
        average_reactivation = self._average(item.reactivation_ratio for item in results)
        average_reconstruction = self._average(item.reconstruction_ratio for item in results)
        average_cognitive = self._average(item.cognitive_reconstruction_score for item in results)
        reactivated_contexts = sum(1 for item in results if item.anchor_count > 0)
        return {
            "reactivation_context_coverage": reactivated_contexts / len(contexts) if contexts else 0.0,
            "reactivation_ratio_avg": average_reactivation,
            "reconstruction_ratio_avg": average_reconstruction,
            "cognitive_reconstruction_score_avg": average_cognitive,
            "contexts": [item.to_dict() for item in results],
        }

    def _evaluate_context(self, context: ContextItem, anchors: list[Anchor]) -> ReactivationResult:
        original_terms = self._terms(context.content)
        anchor_terms = self._terms(" ".join(anchor.text for anchor in anchors))
        reactivated = original_terms & anchor_terms

        reactivation_ratio = len(reactivated) / len(original_terms) if original_terms else 1.0
        reconstruction_ratio = self._reconstruction_ratio(original_terms, anchor_terms)
        anchor_density = min(1.0, len(anchors) / 2.0)
        cognitive_score = (
            0.45 * reactivation_ratio
            + 0.35 * reconstruction_ratio
            + 0.20 * anchor_density
        )

        return ReactivationResult(
            context_id=context.context_id,
            anchor_count=len(anchors),
            original_terms=len(original_terms),
            reactivated_terms=len(reactivated),
            reactivation_ratio=reactivation_ratio,
            reconstruction_ratio=reconstruction_ratio,
            cognitive_reconstruction_score=cognitive_score,
            missing_terms=sorted(original_terms - reactivated),
        )

    def _reconstruction_ratio(self, original_terms: set[str], anchor_terms: set[str]) -> float:
        if not original_terms:
            return 1.0
        if not anchor_terms:
            return 0.0
        direct = len(original_terms & anchor_terms) / len(original_terms)
        semantic_bridge = sum(
            1
            for term in original_terms
            if any(self._soft_match(term, anchor_term) for anchor_term in anchor_terms)
        ) / len(original_terms)
        return min(1.0, direct * 0.75 + semantic_bridge * 0.25)

    def _soft_match(self, left: str, right: str) -> bool:
        if left == right:
            return True
        if len(left) < 5 or len(right) < 5:
            return False
        return left[:5] == right[:5] or left[-5:] == right[-5:]

    def _anchors_by_context(self, anchors: list[Anchor]) -> dict[str, list[Anchor]]:
        grouped: dict[str, list[Anchor]] = {}
        for anchor in anchors:
            grouped.setdefault(anchor.context_id, []).append(anchor)
        return grouped

    def _terms(self, text: str) -> set[str]:
        return {
            self.engine._normalize_token(token)
            for token in re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
            if len(token) >= 4
        } - self.engine._content_terms("a o os as de do da dos das para com que uma um")

    def _average(self, values) -> float:
        items = list(values)
        return sum(items) / len(items) if items else 0.0
