"""Heuristic Bankmap prototype.

This module is intentionally local and dependency-free. It tests the architecture:
many contexts in, semantic anchors selected, one inference packet out, multi-flow
output schema prepared.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
from typing import Any, Literal


STOPWORDS = {
    "a",
    "o",
    "os",
    "as",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "e",
    "em",
    "um",
    "uma",
    "para",
    "por",
    "com",
    "que",
    "se",
    "na",
    "no",
    "nas",
    "nos",
    "ao",
    "aos",
    "eu",
    "vc",
    "voce",
    "isso",
    "essa",
    "esse",
    "esta",
    "estar",
    "ser",
    "foi",
    "sao",
    "mais",
    "menos",
    "muito",
    "pouco",
    "ja",
    "me",
    "minha",
    "meu",
}

DISAMBIGUATION_MARKERS = {
    "nao",
    "mas",
    "porem",
    "porque",
    "pois",
    "entao",
    "logo",
    "se",
    "quando",
    "final",
    "comeco",
    "sentido",
    "contexto",
    "ambiguidade",
    "objetivo",
    "diferente",
    "principal",
}

OPEN_NOEMA_MARKERS = {
    "talvez",
    "pode",
    "poderia",
    "parece",
    "insight",
    "percepcao",
    "perspectiva",
    "almejo",
    "sentido",
    "significa",
}

RISK_MARKERS = {
    "nao",
    "nunca",
    "sem",
    "exceto",
    "apenas",
    "so",
    "depende",
    "risco",
    "erro",
    "errado",
}


@dataclass(slots=True)
class ContextItem:
    """One independent input context before Bankmap fusion."""

    context_id: str
    content: str
    source: str = "user"
    kind: str = "text"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Anchor:
    """High-load semantic anchor extracted from a context."""

    context_id: str
    text: str
    score: float
    decision: str
    reasons: dict[str, float]


@dataclass(slots=True)
class InferencePacket:
    """Context package ready for one LLM call."""

    objective: str
    anchors: list[Anchor]
    compact_context: str
    metrics: dict[str, float]
    audit_trail: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "anchors": [
                {
                    "context_id": anchor.context_id,
                    "text": anchor.text,
                    "score": round(anchor.score, 4),
                    "decision": anchor.decision,
                    "reasons": {k: round(v, 4) for k, v in anchor.reasons.items()},
                }
                for anchor in self.anchors
            ],
            "compact_context": self.compact_context,
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
            "audit_trail": self.audit_trail,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


BankmapMode = Literal["aggressive", "balanced", "coverage"]


class BankmapEngine:
    """Prototype engine for contextual flow compression."""

    def __init__(
        self,
        mode: BankmapMode = "balanced",
        preserve_threshold: float = 0.62,
        summarize_threshold: float = 0.38,
        coverage_floor: float = 0.25,
        max_anchors: int = 6,
    ) -> None:
        self.mode = mode
        defaults = self._mode_defaults(mode)
        self.preserve_threshold = preserve_threshold if preserve_threshold != 0.62 else defaults["preserve_threshold"]
        self.summarize_threshold = summarize_threshold if summarize_threshold != 0.38 else defaults["summarize_threshold"]
        self.coverage_floor = coverage_floor if coverage_floor != 0.25 else defaults["coverage_floor"]
        self.max_anchors = max_anchors

    def _mode_defaults(self, mode: BankmapMode) -> dict[str, float]:
        if mode == "aggressive":
            return {
                "preserve_threshold": 0.68,
                "summarize_threshold": 0.46,
                "coverage_floor": 0.34,
            }
        if mode == "coverage":
            return {
                "preserve_threshold": 0.58,
                "summarize_threshold": 0.34,
                "coverage_floor": 0.20,
            }
        if mode == "balanced":
            return {
                "preserve_threshold": 0.62,
                "summarize_threshold": 0.38,
                "coverage_floor": 0.25,
            }
        raise ValueError(f"Unsupported Bankmap mode: {mode}")

    def build_packet(self, contexts: list[ContextItem], objective: str) -> InferencePacket:
        objective_terms = self._content_terms(objective)
        all_sentences = [sentence for context in contexts for sentence in self._split_sentences(context.content)]
        corpus_freq = self._term_frequency(all_sentences)

        anchors: list[Anchor] = []
        audit_trail: list[dict[str, Any]] = []

        for context in contexts:
            context_anchors = self.extract_anchors(context, objective_terms, corpus_freq)
            anchors.extend(context_anchors)
            audit_trail.append(
                {
                    "context_id": context.context_id,
                    "input_tokens_est": self.estimate_tokens(context.content),
                    "anchors_found": len(context_anchors),
                    "preserved": sum(1 for anchor in context_anchors if anchor.decision == "preserve"),
                    "summarized": sum(1 for anchor in context_anchors if anchor.decision == "summarize"),
                    "open_noemas": sum(1 for anchor in context_anchors if anchor.decision == "open_noema"),
                    "low_signal": sum(1 for anchor in context_anchors if anchor.decision == "low_signal"),
                }
            )

        selected = self._select_anchors(anchors)
        compact_context = self._render_compact_context(selected)

        raw_tokens = sum(self.estimate_tokens(context.content) for context in contexts)
        compact_tokens = self.estimate_tokens(compact_context)
        compression = 1.0 - (compact_tokens / raw_tokens) if raw_tokens else 0.0
        sustaining_contexts = len({anchor.context_id for anchor in selected})

        metrics = {
            "mode": self.mode,
            "contexts_processed": float(len(contexts)),
            "calls_required": 1.0 if contexts else 0.0,
            "contextual_throughput": float(len(contexts)) if contexts else 0.0,
            "raw_tokens_est": float(raw_tokens),
            "compact_tokens_est": float(compact_tokens),
            "token_compression": max(0.0, compression),
            "anchors_selected": float(len(selected)),
            "context_coverage": sustaining_contexts / len(contexts) if contexts else 0.0,
            "semantic_sustentation": self._semantic_sustentation(anchors, selected),
            "structural_lightness": max(0.0, compression) * self._semantic_sustentation(anchors, selected),
        }

        return InferencePacket(
            objective=objective,
            anchors=selected,
            compact_context=compact_context,
            metrics=metrics,
            audit_trail=audit_trail,
        )

    def extract_anchors(
        self,
        context: ContextItem,
        objective_terms: set[str],
        corpus_freq: dict[str, int],
    ) -> list[Anchor]:
        anchors: list[Anchor] = []
        for sentence in self._split_sentences(context.content):
            score, reasons = self._score_sentence(sentence, objective_terms, corpus_freq)
            score *= max(0.1, context.weight)
            decision = self._decision(sentence, score)
            if decision != "remove":
                anchors.append(
                    Anchor(
                        context_id=context.context_id,
                        text=sentence,
                        score=score,
                        decision=decision,
                        reasons=reasons,
                    )
                )
        return anchors

    def simulate_output(self, packet: InferencePacket) -> dict[str, Any]:
        """Return the multi-flow output shape expected from a real LLM later."""

        open_noemas = [anchor.text for anchor in packet.anchors if anchor.decision == "open_noema"]
        return {
            "user_response": self._draft_response(packet),
            "memory_updates": [],
            "activated_noemas": open_noemas,
            "axiom_checks": [
                {
                    "axiom": "preservar_ancoras_de_alta_carga",
                    "status": "checked",
                },
                {
                    "axiom": "nao_confundir_compressao_com_perda_de_sentido",
                    "status": "checked",
                },
            ],
            "audit_trail": packet.audit_trail,
            "quality_checks": self._quality_checks(packet.metrics),
            "next_actions": [
                "Comparar resposta com contexto bruto",
                "Marcar manualmente ancoras corretas em casos de teste",
            ],
            "metrics": self._output_metrics(packet.metrics),
        }

    def simulate_output_json(self, packet: InferencePacket) -> str:
        return json.dumps(self.simulate_output(packet), ensure_ascii=False, indent=2)

    def _score_sentence(
        self,
        sentence: str,
        objective_terms: set[str],
        corpus_freq: dict[str, int],
    ) -> tuple[float, dict[str, float]]:
        terms = self._content_terms(sentence)
        if not terms:
            return 0.0, {}

        centrality = len(terms & objective_terms) / max(1, len(objective_terms))
        disambiguation = len(terms & DISAMBIGUATION_MARKERS) / 3.0
        risk = len(terms & RISK_MARKERS) / 3.0
        open_noema = len(terms & OPEN_NOEMA_MARKERS) / 3.0

        novelty_terms = [term for term in terms if corpus_freq.get(term, 0) <= 1]
        novelty = len(novelty_terms) / max(1, len(terms))

        length = len(terms)
        reconstruction = 1.0 - min(1.0, abs(length - 9) / 12.0)
        redundancy = self._redundancy(terms, corpus_freq)

        raw = (
            0.30 * centrality
            + 0.18 * min(1.0, disambiguation)
            + 0.16 * reconstruction
            + 0.14 * novelty
            + 0.14 * min(1.0, risk)
            + 0.12 * min(1.0, open_noema)
            - 0.16 * redundancy
        )
        score = max(0.0, min(1.0, raw + 0.18))
        return score, {
            "centrality": centrality,
            "disambiguation": min(1.0, disambiguation),
            "reconstruction": reconstruction,
            "novelty": novelty,
            "risk": min(1.0, risk),
            "open_noema": min(1.0, open_noema),
            "redundancy": redundancy,
        }

    def _decision(self, sentence: str, score: float) -> str:
        terms = self._content_terms(sentence)
        if score >= self.preserve_threshold:
            return "open_noema" if terms & OPEN_NOEMA_MARKERS else "preserve"
        if score >= self.summarize_threshold:
            return "summarize"
        if score >= self.coverage_floor:
            return "low_signal"
        return "remove"

    def _render_compact_context(self, anchors: list[Anchor]) -> str:
        return "\n".join(f"- {anchor.text}" for anchor in anchors)

    def _select_anchors(self, anchors: list[Anchor]) -> list[Anchor]:
        candidates = [
            anchor
            for anchor in sorted(anchors, key=lambda item: item.score, reverse=True)
            if anchor.decision in {"preserve", "summarize", "open_noema", "low_signal"}
        ]
        selected: list[Anchor] = []
        selected_keys: set[tuple[str, str]] = set()

        by_context: dict[str, list[Anchor]] = {}
        for anchor in candidates:
            by_context.setdefault(anchor.context_id, []).append(anchor)

        for context_id in sorted(by_context):
            anchor = by_context[context_id][0]
            key = (anchor.context_id, anchor.text)
            selected.append(anchor)
            selected_keys.add(key)

        for anchor in candidates:
            if len(selected) >= self.max_anchors:
                break
            key = (anchor.context_id, anchor.text)
            if key not in selected_keys:
                selected.append(anchor)
                selected_keys.add(key)

        return sorted(selected, key=lambda item: item.score, reverse=True)

    def _semantic_sustentation(self, all_anchors: list[Anchor], selected: list[Anchor]) -> float:
        high_load = [anchor for anchor in all_anchors if anchor.score >= self.summarize_threshold]
        if not high_load:
            return 1.0
        selected_ids = {(anchor.context_id, anchor.text) for anchor in selected}
        preserved = sum(1 for anchor in high_load if (anchor.context_id, anchor.text) in selected_ids)
        return preserved / len(high_load)

    def _draft_response(self, packet: InferencePacket) -> str:
        if not packet.anchors:
            return "Nao ha ancoras suficientes para montar uma resposta sustentada."
        top = packet.anchors[:3]
        core = " | ".join(anchor.text for anchor in top)
        return f"Resposta simulada baseada nas ancoras de maior carga: {core}"

    def _output_metrics(self, metrics: dict[str, float]) -> dict[str, float]:
        return {
            "contextual_throughput": metrics.get("contextual_throughput", 0.0),
            "token_compression_percent": metrics.get("token_compression", 0.0) * 100,
            "context_coverage_percent": metrics.get("context_coverage", 0.0) * 100,
            "semantic_sustentation_percent": metrics.get("semantic_sustentation", 0.0) * 100,
            "structural_lightness_percent": metrics.get("structural_lightness", 0.0) * 100,
            "separability_output_percent": 100.0,
            "semantic_quality_percent": min(100.0, metrics.get("semantic_sustentation", 0.0) * 100),
            "prompt_quality_percent": min(100.0, metrics.get("context_coverage", 0.0) * 70 + metrics.get("token_compression", 0.0) * 30),
            "auditability_percent": 100.0,
        }

    def _quality_checks(self, metrics: dict[str, float]) -> list[dict[str, Any]]:
        compression = metrics.get("token_compression", 0.0) * 100
        coverage = metrics.get("context_coverage", 0.0) * 100
        sustentation = metrics.get("semantic_sustentation", 0.0) * 100
        lightness = metrics.get("structural_lightness", 0.0) * 100
        return [
            {
                "criterion": "preservacao_semantica",
                "score_percent": sustentation,
                "evidence": "Baseado em ancoras de alta carga preservadas no contexto compacto.",
                "risk": "moderado" if sustentation < 70 else "baixo",
            },
            {
                "criterion": "qualidade_do_prompt_compacto",
                "score_percent": min(100.0, coverage * 0.7 + compression * 0.3),
                "evidence": "Combina cobertura de contextos e compressao de tokens.",
                "risk": "baixo" if coverage >= 100 else "moderado",
            },
            {
                "criterion": "leveza_estrutural",
                "score_percent": lightness,
                "evidence": "Compressao ponderada pela sustentacao semantica.",
                "risk": "alto" if lightness < 30 else "moderado",
            },
            {
                "criterion": "auditabilidade",
                "score_percent": 100.0,
                "evidence": "Output preserva ancoras, scores, decisoes e trilha de auditoria.",
                "risk": "baixo",
            },
        ]

    def _split_sentences(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text.strip())
        if not normalized:
            return []
        parts = re.split(r"(?<=[.!?;:])\s+|\n+", normalized)
        return [part.strip(" -\t") for part in parts if part.strip(" -\t")]

    def _content_terms(self, text: str) -> set[str]:
        terms = set()
        for token in re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE):
            token = self._normalize_token(token)
            if len(token) >= 3 and token not in STOPWORDS:
                terms.add(token)
        return terms

    def _term_frequency(self, sentences: list[str]) -> dict[str, int]:
        freq: dict[str, int] = {}
        for sentence in sentences:
            for term in self._content_terms(sentence):
                freq[term] = freq.get(term, 0) + 1
        return freq

    def _redundancy(self, terms: set[str], corpus_freq: dict[str, int]) -> float:
        if not terms:
            return 0.0
        repeated = sum(1 for term in terms if corpus_freq.get(term, 0) > 2)
        return repeated / len(terms)

    def _normalize_token(self, token: str) -> str:
        replacements = str.maketrans(
            {
                "á": "a",
                "à": "a",
                "â": "a",
                "ã": "a",
                "é": "e",
                "ê": "e",
                "í": "i",
                "ó": "o",
                "ô": "o",
                "õ": "o",
                "ú": "u",
                "ç": "c",
            }
        )
        return token.translate(replacements)

    def estimate_tokens(self, text: str) -> int:
        words = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
        punctuation = re.findall(r"[^\w\s]", text, flags=re.UNICODE)
        return max(1, math.ceil(len(words) * 1.25 + len(punctuation) * 0.25)) if text else 0
