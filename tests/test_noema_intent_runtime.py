import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (
    Path(__file__).parents[1]
    / "plugins"
    / "noema-intent-runtime"
    / "scripts"
    / "noema_runtime.py"
)
SPEC = importlib.util.spec_from_file_location("noema_runtime", SCRIPT)
noema_runtime = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(noema_runtime)


class NoemaIntentRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt = """Implementar um validador local para C#.

Criar uma CLI com saída JSON.
Adicionar testes unitários reproduzíveis.
Não usar dependências externas.
Ao terminar, executar todos os testes e entregar o resultado.
"""

    def test_structures_constraints_and_acceptance(self) -> None:
        packet = noema_runtime.structure_intent(self.prompt)

        self.assertEqual(packet["goal"], "Implementar um validador local para C#")
        self.assertIn("Não usar dependências externas", packet["constraints"])
        self.assertTrue(any("testes" in item for item in packet["acceptance"]))
        self.assertEqual(packet["authority"]["original"], "authoritative")

    def test_simple_prompt_is_not_structured(self) -> None:
        self.assertFalse(noema_runtime.should_structure("Explique esta função."))

    def test_single_line_prompt_is_split_without_duplicate_full_text(self) -> None:
        prompt = (
            "Implementar um módulo local. Criar testes reproduzíveis. "
            "Não usar APIs externas. Ao terminar, validar os resultados."
        )
        packet = noema_runtime.structure_intent(prompt)

        self.assertEqual(packet["goal"], "Implementar um módulo local")
        self.assertEqual(packet["constraints"], ["Não usar APIs externas"])
        self.assertIn("Ao terminar, validar os resultados", packet["acceptance"])

    def test_prompt_comparison_subtracts_both_directions(self) -> None:
        result = noema_runtime.compare_prompt_cost(self.prompt * 3)

        self.assertTrue(result["structured"])
        self.assertEqual(
            result["delta_tokens"],
            result["assisted_tokens"] - result["baseline_tokens"],
        )
        self.assertEqual(result["net_savings_tokens"], -result["delta_tokens"])

    def test_actual_comparison_reports_net_savings(self) -> None:
        result = noema_runtime.compare_actual(1000, 400, 800, 300)

        self.assertEqual(result["baseline"]["total_tokens"], 1400)
        self.assertEqual(result["assisted"]["total_tokens"], 1100)
        self.assertEqual(result["delta_tokens"], -300)
        self.assertEqual(result["net_savings_tokens"], 300)

    def test_hook_injects_packet_without_prompt_content_in_telemetry(self) -> None:
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "session-secret",
            "turn_id": "turn-secret",
            "model": "test-model",
            "prompt": self.prompt * 3,
        }
        captured = []
        with patch.object(
            noema_runtime, "_write_telemetry", side_effect=captured.append
        ):
            output = noema_runtime.handle_hook(payload)
        event = noema_runtime._base_event(payload)

        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("NOEMA_INTENT_PACKET", context)
        self.assertNotIn("prompt", event)
        self.assertNotIn("session-secret", str(event))
        self.assertNotIn("turn-secret", str(event))
        self.assertNotIn(self.prompt, str(captured))

    def test_baseline_mode_records_without_injecting(self) -> None:
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "baseline-session",
            "turn_id": "baseline-turn",
            "model": "test-model",
            "prompt": self.prompt * 3,
        }
        captured = []
        with patch.dict("os.environ", {"NOEMA_EXPERIMENT_MODE": "baseline"}), patch.object(
            noema_runtime, "_write_telemetry", side_effect=captured.append
        ):
            output = noema_runtime.handle_hook(payload)

        self.assertEqual(output, {})
        self.assertEqual(captured[0]["mode"], "baseline")
        self.assertFalse(captured[0]["injected"])

    def test_summary_aggregates_without_content(self) -> None:
        events = [
            {
                "kind": "prompt",
                "session_hash": "a",
                "mode": "assisted",
                "baseline_tokens": 100,
                "assisted_tokens": 130,
                "observed_prompt_tokens": 130,
                "structured": True,
            },
            {
                "kind": "tool",
                "session_hash": "a",
                "mode": "assisted",
                "tool_name": "Bash",
            },
            {
                "kind": "stop",
                "session_hash": "a",
                "mode": "assisted",
                "response_estimated_tokens": 20,
            },
        ]
        summary = noema_runtime.summarize_events(events)

        self.assertEqual(summary["sessions"], 1)
        self.assertEqual(summary["delta_prompt_tokens"], 30)
        self.assertEqual(summary["net_prompt_savings_tokens"], -30)
        self.assertEqual(summary["tool_calls"], 1)

    def test_summary_subtracts_baseline_and_assisted_tasks(self) -> None:
        events = [
            {
                "kind": "prompt",
                "mode": "baseline",
                "session_hash": "baseline",
                "observed_prompt_tokens": 100,
            },
            {
                "kind": "stop",
                "mode": "baseline",
                "session_hash": "baseline",
                "response_estimated_tokens": 40,
            },
            {
                "kind": "prompt",
                "mode": "assisted",
                "session_hash": "assisted",
                "observed_prompt_tokens": 110,
            },
            {
                "kind": "stop",
                "mode": "assisted",
                "session_hash": "assisted",
                "response_estimated_tokens": 20,
            },
        ]
        summary = noema_runtime.summarize_events(events)

        self.assertTrue(summary["ab_comparison_available"])
        self.assertEqual(summary["estimated_task_delta_tokens"], -10)
        self.assertEqual(summary["estimated_task_net_savings_tokens"], 10)


if __name__ == "__main__":
    unittest.main()
