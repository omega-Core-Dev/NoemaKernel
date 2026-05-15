import unittest

from noemakernel import ContextJudge, ContextItem, judge_context


def context_with_metrics(context_id: str, metrics: dict[str, float]) -> dict:
    return {
        "context_id": context_id,
        "context_text": "Contexto controlado para teste.",
        "metrics": metrics,
    }


class ContextJudgeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.query = "Como preservar contexto progressivo no Bankmap?"
        self.state = {"recency": 1.0}

    def test_highly_relevant_context_is_promoted(self) -> None:
        result = judge_context(
            context_with_metrics(
                "high",
                {
                    "relevance": 1.0,
                    "coherence": 1.0,
                    "confidence": 1.0,
                    "recency": 1.0,
                    "semantic_power": 1.0,
                },
            ),
            self.query,
            self.state,
        )

        self.assertEqual(result.decision, "promote")
        self.assertEqual(result.color_state, "green")
        self.assertEqual(result.judge_score, 1.0)
        self.assertIn("semantic_power", result.to_dict()["terms"])

    def test_redundant_context_is_penalized(self) -> None:
        result = judge_context(
            context_with_metrics(
                "redundant",
                {
                    "relevance": 0.9,
                    "coherence": 0.8,
                    "confidence": 0.8,
                    "recency": 0.6,
                    "semantic_power": 0.4,
                    "redundancy_penalty": 1.0,
                },
            ),
            self.query,
            self.state,
        )

        self.assertLess(result.weighted_terms["redundancy_penalty"], 0.0)
        self.assertEqual(result.decision, "compact")

    def test_contradictory_context_goes_to_audit(self) -> None:
        result = judge_context(
            context_with_metrics(
                "contradiction",
                {
                    "relevance": 0.8,
                    "coherence": 0.8,
                    "confidence": 0.7,
                    "recency": 0.6,
                    "semantic_power": 0.45,
                    "contradiction_penalty": 1.0,
                },
            ),
            self.query,
            self.state,
        )

        self.assertEqual(result.decision, "audit")
        self.assertIn("contradiction", result.repair_instruction.lower())

    def test_noisy_context_is_penalized(self) -> None:
        result = judge_context(
            context_with_metrics(
                "noise",
                {
                    "relevance": 0.65,
                    "coherence": 0.55,
                    "confidence": 0.55,
                    "recency": 0.5,
                    "semantic_power": 0.25,
                    "noise_penalty": 1.0,
                },
            ),
            self.query,
            self.state,
        )

        self.assertEqual(result.decision, "audit")
        self.assertIn("noisy", result.repair_instruction.lower())

    def test_disposable_context_is_discarded(self) -> None:
        result = judge_context(
            context_with_metrics(
                "weak",
                {
                    "relevance": 0.1,
                    "coherence": 0.2,
                    "confidence": 0.1,
                    "recency": 0.1,
                    "semantic_power": 0.0,
                    "noise_penalty": 0.4,
                },
            ),
            self.query,
            self.state,
        )

        self.assertEqual(result.decision, "discard")
        self.assertEqual(result.color_state, "red")

    def test_score_above_one_is_clipped(self) -> None:
        result = judge_context(
            context_with_metrics(
                "clip-high",
                {
                    "relevance": 2.0,
                    "coherence": 2.0,
                    "confidence": 2.0,
                    "recency": 2.0,
                    "semantic_power": 2.0,
                },
            ),
            self.query,
            self.state,
            weights={
                "relevance": 1.0,
                "coherence": 1.0,
                "confidence": 1.0,
                "recency": 1.0,
                "semantic_power": 1.0,
            },
        )

        self.assertEqual(result.judge_score, 1.0)

    def test_score_below_zero_is_clipped(self) -> None:
        result = judge_context(
            context_with_metrics(
                "clip-low",
                {
                    "redundancy_penalty": 2.0,
                    "noise_penalty": 2.0,
                    "contradiction_penalty": 2.0,
                },
            ),
            self.query,
            self.state,
            weights={
                "redundancy_penalty": 1.0,
                "noise_penalty": 1.0,
                "contradiction_penalty": 1.0,
            },
        )

        self.assertEqual(result.judge_score, 0.0)
        self.assertEqual(result.decision, "discard")

    def test_infers_metrics_from_context_item(self) -> None:
        context = ContextItem(
            context_id="c1",
            content="Bankmap preserva ancoras que ativam o contexto progressivo seguinte.",
        )
        result = ContextJudge().judge_context(
            context,
            self.query,
            {
                "future_contexts": [
                    "O contexto progressivo seguinte mede ativacao de ancoras do Bankmap."
                ],
                "previous_contexts": [],
                "position": 0,
                "total_contexts": 2,
            },
        )

        self.assertGreater(result.terms["semantic_power"], 0.0)
        self.assertIn(result.decision, {"promote", "compact", "audit", "discard"})

    def test_accepts_custom_thresholds(self) -> None:
        result = judge_context(
            context_with_metrics(
                "threshold",
                {
                    "relevance": 0.6,
                    "coherence": 0.6,
                    "confidence": 0.6,
                    "recency": 0.6,
                    "semantic_power": 0.6,
                },
            ),
            self.query,
            self.state,
            thresholds={"promote": 0.7, "compact": 0.55, "audit": 0.45},
        )

        self.assertEqual(result.decision, "compact")


if __name__ == "__main__":
    unittest.main()
