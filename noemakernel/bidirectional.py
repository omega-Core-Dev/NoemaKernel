"""Bidirectional context metrics: regressive + progressive."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .bankmap import Anchor, BankmapEngine, ContextItem, InferencePacket


@dataclass(slots=True)
class BidirectionalContextResult:
    anchor_text: str
    context_id: str
    regressive_score: float
    progressive_score: float
    bidirectional_score: float
    direction: str

    def to_dict(self) -> dict:
        return {
            "context_id": self.context_id,
            "anchor_text": self.anchor_text,
            "regressive_score": self.regressive_score,
            "progressive_score": self.progressive_score,
            "bidirectional_score": self.bidirectional_score,
            "direction": self.direction,
        }


class BidirectionalEvaluator:
    """Evaluate anchors by past sustentation and future activation."""

    def __init__(self) -> None:
        self.engine = BankmapEngine()

    def evaluate(self, contexts: list[ContextItem], packet: InferencePacket, objective: str) -> dict:
        context_order = {context.context_id: index for index, context in enumerate(contexts)}
        context_terms = [self._terms(context.content) for context in contexts]
        objective_terms = self._terms(objective)

        results = [
            self._evaluate_anchor(anchor, context_order, context_terms, objective_terms)
            for anchor in packet.anchors
        ]
        stable = [item for item in results if item.direction == "bidirectional"]
        return {
            "anchors_evaluated": len(results),
            "bidirectional_stability": len(stable) / len(results) if results else 0.0,
            "regressive_score_avg": self._average(item.regressive_score for item in results),
            "progressive_score_avg": self._average(item.progressive_score for item in results),
            "bidirectional_score_avg": self._average(item.bidirectional_score for item in results),
            "anchors": [item.to_dict() for item in results],
        }

    def _evaluate_anchor(
        self,
        anchor: Anchor,
        context_order: dict[str, int],
        context_terms: list[set[str]],
        objective_terms: set[str],
    ) -> BidirectionalContextResult:
        index = context_order.get(anchor.context_id, 0)
        anchor_terms = self._terms(anchor.text)
        previous_terms = set().union(*context_terms[: index + 1]) if context_terms[: index + 1] else set()
        future_terms = set().union(*context_terms[index + 1 :]) if context_terms[index + 1 :] else set()

        regressive = self._overlap(anchor_terms, previous_terms | objective_terms)
        progressive = self._overlap(anchor_terms | objective_terms, future_terms)
        bidirectional = (regressive * 0.55) + (progressive * 0.45)
        direction = self._direction(regressive, progressive)

        return BidirectionalContextResult(
            anchor_text=anchor.text,
            context_id=anchor.context_id,
            regressive_score=regressive,
            progressive_score=progressive,
            bidirectional_score=bidirectional,
            direction=direction,
        )

    def _direction(self, regressive: float, progressive: float) -> str:
        if regressive >= 0.45 and progressive >= 0.25:
            return "bidirectional"
        if regressive >= progressive:
            return "regressive"
        return "progressive"

    def _overlap(self, left: set[str], right: set[str]) -> float:
        if not left:
            return 0.0
        return len(left & right) / len(left)

    def _terms(self, text: str) -> set[str]:
        return {
            self.engine._normalize_token(token)
            for token in re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
            if len(token) >= 4
        }

    def _average(self, values) -> float:
        items = list(values)
        return sum(items) / len(items) if items else 0.0
