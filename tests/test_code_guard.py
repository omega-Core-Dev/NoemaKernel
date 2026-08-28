import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from noemakernel.code_guard import analyze_source, main


class CodeGuardTest(unittest.TestCase):
    def test_valid_csharp_verbatim_string(self) -> None:
        source = '''class Example
{
    string Path = @"C:\\temp\\file.txt";
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["candidate"])

    def test_doubled_quotes_are_valid_in_verbatim_string(self) -> None:
        source = '''class Example
{
    string Message = @"She said ""hello"".";
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "ok")
        self.assertIsNone(result["candidate"])

    def test_embedded_javascript_regex_quote_is_reported(self) -> None:
        source = '''class Example
{
    string Script = @"const clean = value.replace(/"/g, '\\"');";
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(
            result["candidate"]["rule"],
            "unescaped_quote_in_verbatim_string",
        )
        self.assertEqual(result["candidate"]["line"], 3)
        self.assertIn('replace(/"/g', result["candidate"]["evidence"])

    def test_unclosed_verbatim_string_is_reported(self) -> None:
        source = '''class Example
{
    string Message = @"truncated
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["candidate"]["rule"], "unclosed_verbatim_string")
        self.assertEqual(result["candidate"]["line"], 3)

    def test_global_anchor_discovery_is_recorded(self) -> None:
        source = '''class Example
{
    string Message = "truncated
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["candidate"]["rule"], "unclosed_string")
        self.assertTrue(result["escalated"])
        self.assertEqual(
            result["escalation_reason"],
            "no_verbatim_anchor_required_global_discovery",
        )

    def test_local_cause_does_not_analyze_entire_file(self) -> None:
        prefix = "\n".join(f"// prefix {number}" for number in range(1, 121))
        suffix = "\n".join(f"// suffix {number}" for number in range(1, 121))
        source = f'''{prefix}
class Example
{{
    void Build()
    {{
        string Script = @"value.replace(/"/g, ""x"");";
    }}
}}
{suffix}
'''
        result = analyze_source(source, error_line=125)

        self.assertEqual(result["status"], "blocked")
        self.assertLess(result["lines_analyzed"], len(source.splitlines()))
        self.assertGreaterEqual(result["scope"]["start_line"], 121)
        self.assertFalse(result["escalated"])

    def test_whole_file_expansion_is_recorded(self) -> None:
        source = '''class First
{
    string Message = @"valid";
}

class Second
{
    string Message = @"also valid";
}
'''
        result = analyze_source(source)

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["escalated"])
        self.assertEqual(
            result["escalation_reason"],
            "local_scope_had_no_sufficient_evidence",
        )
        self.assertEqual(result["scope"]["start_line"], 1)
        self.assertEqual(result["scope"]["end_line"], len(source.splitlines()))

    def test_cli_outputs_json(self) -> None:
        source = 'class Example { string Script = @"replace(/"/g, ""x"");"; }'
        output = io.StringIO()
        with patch(
            "noemakernel.code_guard.analyze_file",
            return_value=analyze_source(source),
        ), redirect_stdout(output):
            return_code = main(["Broken.cs"])

        result = json.loads(output.getvalue())
        self.assertEqual(return_code, 1)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["language"], "csharp")
        self.assertEqual(result["strategy"], "asymmetric-local-scan")


if __name__ == "__main__":
    unittest.main()
