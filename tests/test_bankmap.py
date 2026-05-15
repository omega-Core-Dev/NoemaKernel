import unittest
from unittest.mock import Mock, patch

from noemakernel import BankmapEngine, ContextItem
from noemakernel.gemma_api import GemmaApiClient
from noemakernel.prompts import build_bankmap_prompt, build_raw_prompt
from noemakernel.gemma_api import extract_text
from noemakernel.openai_api import extract_response_text
from noemakernel.validation import parse_json_output, validate_multiflow_output


class BankmapEngineTest(unittest.TestCase):
    def test_build_packet_selects_anchors_and_compresses(self) -> None:
        contexts = [
            ContextItem(
                context_id="a",
                content="O Bankmap organiza muitos contextos em uma unica inferencia.",
            ),
            ContextItem(
                context_id="b",
                content="Nao basta reduzir tokens; precisa preservar sentido e contexto.",
            ),
        ]
        engine = BankmapEngine()
        packet = engine.build_packet(contexts, "reduzir tokens preservando contexto")

        self.assertGreaterEqual(len(packet.anchors), 1)
        self.assertIn("token_compression", packet.metrics)
        self.assertGreaterEqual(packet.metrics["semantic_sustentation"], 0.0)
        self.assertLessEqual(packet.metrics["semantic_sustentation"], 1.0)

    def test_simulated_output_has_expected_flows(self) -> None:
        contexts = [
            ContextItem(
                context_id="a",
                content="Frases curtas podem carregar contexto inteiro e mudar a resposta.",
            )
        ]
        engine = BankmapEngine()
        packet = engine.build_packet(contexts, "identificar ancoras semanticas")
        output = engine.simulate_output(packet)

        expected = {
            "user_response",
            "memory_updates",
            "activated_noemas",
            "axiom_checks",
            "audit_trail",
            "quality_checks",
            "next_actions",
            "metrics",
        }
        self.assertEqual(set(output), expected)
        self.assertIn("token_compression_percent", output["metrics"])

    def test_prompt_builders_include_schema(self) -> None:
        contexts = [ContextItem(context_id="a", content="Contexto pequeno.")]
        engine = BankmapEngine()
        packet = engine.build_packet(contexts, "testar prompt")

        self.assertIn("Schema obrigatorio", build_raw_prompt(contexts, "testar prompt"))
        self.assertIn("Bankmap Compacto", build_bankmap_prompt(packet))

    def test_validate_multiflow_output(self) -> None:
        text = """{
          "user_response": "ok",
          "memory_updates": [],
          "activated_noemas": [],
          "axiom_checks": [],
          "audit_trail": [],
          "quality_checks": [],
          "next_actions": [],
          "metrics": {}
        }"""
        parsed, errors = parse_json_output(text)
        self.assertEqual(errors, [])
        result = validate_multiflow_output(parsed)
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["separability_output"], 1.0)

    def test_parse_json_from_mixed_output(self) -> None:
        text = """explicacao antes
        {"user_response":"ok","memory_updates":[],"activated_noemas":[],"axiom_checks":[],"audit_trail":[],"quality_checks":[],"next_actions":[],"metrics":{}}
        comentario depois"""
        parsed, errors = parse_json_output(text)
        self.assertEqual(errors, [])
        self.assertEqual(parsed["user_response"], "ok")

    def test_parse_json_after_brace_mentions(self) -> None:
        text = """First char `{`, last char `}`? Yes.{
          "user_response":"ok",
          "memory_updates":[],
          "activated_noemas":[],
          "axiom_checks":[],
          "audit_trail":[],
          "quality_checks":[],
          "next_actions":[],
          "metrics":{}
        }"""
        parsed, errors = parse_json_output(text)
        self.assertEqual(errors, [])
        self.assertEqual(parsed["user_response"], "ok")

    def test_extract_gemma_text(self) -> None:
        response = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": '{"user_response":"ok"}'}],
                    }
                }
            ]
        }
        self.assertEqual(extract_text(response), '{"user_response":"ok"}')

    def test_extract_openai_response_text(self) -> None:
        response = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": '{"user_response":"ok"}'}
                    ]
                }
            ]
        }
        self.assertEqual(extract_response_text(response), '{"user_response":"ok"}')

    def test_gemma_generate_can_disable_json_mime_type(self) -> None:
        client = GemmaApiClient(api_key="key", model="gemma-test")
        fake_response = Mock()
        fake_response.__enter__ = Mock(
            return_value=Mock(
                read=Mock(
                    return_value=b'{"candidates":[{"content":{"parts":[{"text":"ok"}]}}]}'
                )
            )
        )
        fake_response.__exit__ = Mock(return_value=None)

        with patch("urllib.request.urlopen", return_value=fake_response), patch(
            "urllib.request.Request"
        ) as request:
            self.assertEqual(client.generate("hello", response_mime_type=None), "ok")

        payload = request.call_args.kwargs["data"].decode("utf-8")
        self.assertNotIn("responseMimeType", payload)


if __name__ == "__main__":
    unittest.main()
