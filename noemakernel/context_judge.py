"""Auditable context judge for Bankmap contexts."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Mapping

from .bankmap import BankmapEngine, ContextItem


LLM_CONTINUOUS_WEIGHTS = {
    "relevance": 0.25,
    "coherence": 0.20,
    "confidence": 0.25,
    "recency": 0.05,
    "semantic_power": 0.45,
    "redundancy_penalty": 0.08,
    "noise_penalty": 0.25,
    "contradiction_penalty": 0.30,
}

DEFAULT_THRESHOLDS = {
    "promote": 0.85,
    "compact": 0.60,
    "audit": 0.35,
}

LLM_CONTINUOUS_THRESHOLDS = {
    "promote": 0.82,
    "compact": 0.60,
    "audit": 0.45,
}

POSITIVE_TERMS = (
    "relevance",
    "coherence",
    "confidence",
    "recency",
    "semantic_power",
)
PENALTY_TERMS = (
    "redundancy_penalty",
    "noise_penalty",
    "contradiction_penalty",
)
ALL_TERMS = POSITIVE_TERMS + PENALTY_TERMS


@dataclass(slots=True)
class JudgeWeights:
    relevance: float = 0.30
    coherence: float = 0.25
    confidence: float = 0.15
    recency: float = 0.10
    semantic_power: float = 0.20
    redundancy_penalty: float = 0.10
    noise_penalty: float = 0.15
    contradiction_penalty: float = 0.25

    @classmethod
    def from_mapping(cls, values: Mapping[str, float] | None = None) -> "JudgeWeights":
        if values is None:
            return cls()
        defaults = cls()
        data = {
            name: float(values.get(name, getattr(defaults, name)))
            for name in ALL_TERMS
        }
        return cls(**data)


@dataclass(slots=True)
class JudgeThresholds:
    promote: float = 0.85
    compact: float = 0.60
    audit: float = 0.35

    @classmethod
    def from_mapping(cls, values: Mapping[str, float] | None = None) -> "JudgeThresholds":
        if values is None:
            return cls()
        defaults = cls()
        return cls(
            promote=float(values.get("promote", defaults.promote)),
            compact=float(values.get("compact", defaults.compact)),
            audit=float(values.get("audit", defaults.audit)),
        )


@dataclass(slots=True)
class JudgeResult:
    context_id: str
    judge_score: float
    decision: str
    color_state: str
    terms: dict[str, float] = field(default_factory=dict)
    weighted_terms: dict[str, float] = field(default_factory=dict)
    audit_reason: str = ""
    repair_instruction: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "judge_score": round(self.judge_score, 4),
            "decision": self.decision,
            "color_state": self.color_state,
            "terms": {key: round(value, 4) for key, value in self.terms.items()},
            "weighted_terms": {
                key: round(value, 4) for key, value in self.weighted_terms.items()
            },
            "audit_reason": self.audit_reason,
            "repair_instruction": self.repair_instruction,
        }


class ContextJudge:
    """Judge whether a context block should be used by Bankmap."""

    def __init__(
        self,
        weights: Mapping[str, float] | None = None,
        thresholds: Mapping[str, float] | None = None,
        profile: str = "default",
    ) -> None:
        if weights is None and profile == "llm_continuous":
            weights = LLM_CONTINUOUS_WEIGHTS
        if thresholds is None and profile == "llm_continuous":
            thresholds = LLM_CONTINUOUS_THRESHOLDS
        self.weights = JudgeWeights.from_mapping(weights)
        self.thresholds = JudgeThresholds.from_mapping(thresholds)
        self.profile = profile
        self.engine = BankmapEngine()

    def judge_context(
        self,
        context_item: ContextItem | Mapping[str, Any],
        query: str,
        system_state: Mapping[str, Any] | None = None,
        weights: Mapping[str, float] | None = None,
        thresholds: Mapping[str, float] | None = None,
    ) -> JudgeResult:
        context_id, context_text, explicit_metrics = self._unpack_context(context_item)
        state = system_state or {}
        metrics = explicit_metrics or self._infer_metrics(context_text, query, state)
        terms = self._normalize_metrics(metrics)
        active_weights = JudgeWeights.from_mapping(weights) if weights else self.weights
        active_thresholds = (
            JudgeThresholds.from_mapping(thresholds) if thresholds else self.thresholds
        )
        weighted_terms = self._weighted_terms(terms, active_weights)
        score = self._clip(sum(weighted_terms.values()))
        decision = self._decision(score, active_thresholds)

        return JudgeResult(
            context_id=context_id,
            judge_score=score,
            decision=decision,
            color_state=self._color_state(decision),
            terms=terms,
            weighted_terms=weighted_terms,
            audit_reason=self._audit_reason(terms, weighted_terms, score, decision),
            repair_instruction=self._repair_instruction(terms, decision),
        )

    def _unpack_context(
        self, context_item: ContextItem | Mapping[str, Any]
    ) -> tuple[str, str, Mapping[str, float] | None]:
        if isinstance(context_item, ContextItem):
            return (
                context_item.context_id,
                context_item.content,
                context_item.metadata.get("judge_metrics"),
            )

        context_id = str(context_item.get("context_id", "unknown"))
        context_text = str(context_item.get("context_text", context_item.get("content", "")))
        metrics = context_item.get("metrics") or context_item.get("judge_metrics")
        return context_id, context_text, metrics

    def _normalize_metrics(self, metrics: Mapping[str, float]) -> dict[str, float]:
        return {
            name: self._clip(float(metrics.get(name, 0.0)))
            for name in ALL_TERMS
        }

    def _weighted_terms(
        self, terms: Mapping[str, float], weights: JudgeWeights
    ) -> dict[str, float]:
        weighted = {
            name: terms[name] * getattr(weights, name)
            for name in POSITIVE_TERMS
        }
        weighted.update(
            {
                name: -terms[name] * getattr(weights, name)
                for name in PENALTY_TERMS
            }
        )
        return weighted

    def _infer_metrics(
        self,
        context_text: str,
        query: str,
        system_state: Mapping[str, Any],
    ) -> dict[str, float]:
        context_terms = self._terms(context_text)
        query_terms = self._terms(query)
        future_terms = self._terms(" ".join(system_state.get("future_contexts", [])))
        previous_terms = self._terms(" ".join(system_state.get("previous_contexts", [])))

        relevance = self._relevance(query_terms, context_terms, future_terms)
        progressive_activation = self._overlap(context_terms | query_terms, future_terms)
        novelty = 1.0 - self._overlap(context_terms, previous_terms)
        semantic_power = self._clip(
            (progressive_activation * 0.65)
            + (novelty * 0.15)
            + (relevance * 0.20)
            + self._marker_power(context_text)
        )

        noise_penalty = self._noise_penalty(context_text, context_terms)
        redundancy_penalty = self._clip(self._overlap(context_terms, previous_terms) * 0.75)
        contradiction_penalty = self._contradiction_penalty(context_text, query)
        coherence = self._coherence(context_text, context_terms, noise_penalty)
        confidence = self._clip((relevance * 0.35) + (coherence * 0.30) + (semantic_power * 0.35))
        recency = self._recency(system_state)

        return {
            "relevance": relevance,
            "coherence": coherence,
            "confidence": confidence,
            "recency": recency,
            "semantic_power": semantic_power,
            "redundancy_penalty": redundancy_penalty,
            "noise_penalty": noise_penalty,
            "contradiction_penalty": contradiction_penalty,
        }

    def _decision(self, score: float, thresholds: JudgeThresholds) -> str:
        if score >= thresholds.promote:
            return "promote"
        if score >= thresholds.compact:
            return "compact"
        if score >= thresholds.audit:
            return "audit"
        return "discard"

    def _color_state(self, decision: str) -> str:
        return {
            "promote": "green",
            "compact": "yellow_green",
            "audit": "yellow",
            "discard": "red",
        }[decision]

    def _audit_reason(
        self,
        terms: Mapping[str, float],
        weighted_terms: Mapping[str, float],
        score: float,
        decision: str,
    ) -> str:
        strongest_positive = max(POSITIVE_TERMS, key=lambda name: weighted_terms[name])
        strongest_penalty = min(PENALTY_TERMS, key=lambda name: weighted_terms[name])
        return (
            f"Semantic Sustainment Score={score:.2f}; decision={decision}; "
            f"strongest_positive={strongest_positive}:{terms[strongest_positive]:.2f}; "
            f"strongest_penalty={strongest_penalty}:{terms[strongest_penalty]:.2f}."
        )

    def _repair_instruction(self, terms: Mapping[str, float], decision: str) -> str:
        if decision == "promote":
            return "Use as high-sustainment context."
        if terms["contradiction_penalty"] >= 0.45:
            return "Isolate contradiction before generation and request resolution."
        if terms["noise_penalty"] >= 0.45:
            return "Clean noisy fragments before compacting this context."
        if terms["redundancy_penalty"] >= 0.45:
            return "Merge with prior context or keep only novel anchors."
        if decision == "compact":
            return "Compact while preserving semantic anchors and progressive links."
        if decision == "audit":
            return "Keep out of generation path until reviewed or repaired."
        return "Discard for this query unless new evidence raises relevance."

    def _coherence(self, text: str, terms: set[str], noise_penalty: float) -> float:
        if not text.strip():
            return 0.0
        term_density = min(1.0, len(terms) / 12.0)
        sentence_count = max(1, len(re.findall(r"[.!?;:]", text)))
        sentence_balance = 1.0 - min(1.0, abs(sentence_count - 2) / 6.0)
        return self._clip((term_density * 0.55) + (sentence_balance * 0.30) + ((1 - noise_penalty) * 0.15))

    def _noise_penalty(self, text: str, terms: set[str]) -> float:
        if not text:
            return 1.0
        symbols = len(re.findall(r"[^A-Za-zÀ-ÿ0-9\s.,;:!?_-]", text))
        symbol_ratio = symbols / max(1, len(text))
        short_text_noise = 0.35 if len(terms) <= 1 else 0.0
        repeated_chars = 0.25 if re.search(r"(.)\1{4,}", text) else 0.0
        explicit_noise = 0.35 if self._terms(text) & {"ruido", "irrelevante", "enchimento"} else 0.0
        return self._clip(symbol_ratio * 5.0 + short_text_noise + repeated_chars + explicit_noise)

    def _contradiction_penalty(self, context_text: str, query: str) -> float:
        context_terms = self._terms(context_text)
        query_terms = self._terms(query)
        contradiction_terms = {"conflito", "contradiz", "impossivel", "falso", "inverso"}
        if context_terms & query_terms and self._terms(context_text) & contradiction_terms:
            return 0.55
        return 0.0

    def _relevance(
        self,
        query_terms: set[str],
        context_terms: set[str],
        future_terms: set[str],
    ) -> float:
        direct = self._overlap(query_terms, context_terms)
        future_bridge = self._overlap(query_terms, future_terms & context_terms)
        context_bridge = self._overlap(context_terms, future_terms)
        return self._clip((direct * 0.65) + (future_bridge * 0.20) + (context_bridge * 0.15))

    def _marker_power(self, text: str) -> float:
        marker_terms = {
            "bankmap",
            "contexto",
            "contextual",
            "ancora",
            "ancoras",
            "semantica",
            "sustentacao",
            "compressao",
            "auditabilidade",
            "metricas",
            "output",
            "fluxos",
            "progressivo",
            "regressivo",
            "bidirecional",
        }
        hits = len(self._terms(text) & marker_terms)
        return min(0.18, hits * 0.035)

    def _recency(self, system_state: Mapping[str, Any]) -> float:
        if "recency" in system_state:
            return self._clip(float(system_state["recency"]))
        if "position" in system_state and "total_contexts" in system_state:
            total = max(1.0, float(system_state["total_contexts"]) - 1.0)
            return self._clip(float(system_state["position"]) / total)
        return 0.5

    def _terms(self, text: str) -> set[str]:
        return self.engine._content_terms(text)

    def _overlap(self, left: set[str], right: set[str]) -> float:
        if not left:
            return 0.0
        return len(left & right) / len(left)

    def _clip(self, value: float) -> float:
        return max(0.0, min(1.0, value))


def judge_context(
    context_item: ContextItem | Mapping[str, Any],
    query: str,
    system_state: Mapping[str, Any] | None = None,
    weights: Mapping[str, float] | None = None,
    thresholds: Mapping[str, float] | None = None,
) -> JudgeResult:
    """Convenience wrapper for the default ContextJudge."""

    return ContextJudge(weights=weights, thresholds=thresholds).judge_context(
        context_item,
        query,
        system_state,
    )
