"""Local structural validation for C# source files.

The validator intentionally favors a small syntactic neighborhood over a full
parser.  It is an MVP guard for catching likely truncation around C# strings,
especially verbatim strings containing embedded source code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


STRATEGY = "asymmetric-local-scan"
DEFAULT_RADIUS = 80


def analyze_file(path: str | Path, error_line: int | None = None) -> dict[str, Any]:
    """Analyze a C# file and return a JSON-serializable diagnostic."""

    source_path = Path(path)
    try:
        source = source_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return _result(
            status="blocked",
            scope=(0, 0),
            candidate={
                "line": 0,
                "rule": "file_read_error",
                "evidence": str(exc),
            },
            recommended_action="Verify that the file exists and is UTF-8 encoded.",
            escalated=False,
            escalation_reason=None,
        )

    return analyze_source(source, error_line=error_line)


def analyze_source(source: str, error_line: int | None = None) -> dict[str, Any]:
    """Analyze C# source, beginning at an optional compiler error line."""

    lines = source.splitlines()
    if not lines:
        return _result(
            status="ok",
            scope=(0, 0),
            candidate=None,
            recommended_action="No structural issue detected.",
            escalated=False,
            escalation_reason=None,
        )

    anchor, anchor_source, discovery_escalated = _select_anchor(lines, error_line)
    start, end = _find_local_scope(lines, anchor)
    candidate = _scan_scope(lines, start, end)
    escalated = discovery_escalated
    escalation_reason = (
        "no_verbatim_anchor_required_global_discovery"
        if discovery_escalated
        else None
    )

    if candidate is None and (start > 1 or end < len(lines)):
        # The local hypothesis was insufficient. A whole-file structural pass
        # is allowed only after recording the escalation in the result.
        escalated = True
        escalation_reason = "local_scope_had_no_sufficient_evidence"
        start, end = 1, len(lines)
        candidate = _scan_scope(lines, start, end)

    if candidate is not None:
        return _result(
            status="blocked",
            scope=(start, end),
            candidate=candidate,
            recommended_action=_recommendation(candidate["rule"]),
            escalated=escalated,
            escalation_reason=escalation_reason,
            anchor_source=anchor_source,
        )

    return _result(
        status="warning" if escalated and error_line is not None else "ok",
        scope=(start, end),
        candidate=None,
        recommended_action=(
            "Review the compiler diagnostic; the local scan found no structural cause."
            if escalated
            else "No structural issue detected in the analyzed block."
        ),
        escalated=escalated,
        escalation_reason=escalation_reason,
        anchor_source=anchor_source,
    )


def _select_anchor(
    lines: list[str], error_line: int | None
) -> tuple[int, str, bool]:
    if error_line is not None:
        return max(1, min(error_line, len(lines))), "compiler_error_line", False

    first_start = next(iter(_verbatim_start_lines(lines)), None)
    if first_start is not None:
        return first_start, "first_verbatim_string", False
    # Establishing that there is no verbatim-string anchor inspects every line.
    # Record that global discovery even though structural validation stays local.
    return 1, "file_start", True


def _verbatim_start_lines(lines: Iterable[str]) -> Iterable[int]:
    for number, line in enumerate(lines, start=1):
        if '@"' in line:
            yield number


def _find_local_scope(lines: list[str], anchor: int) -> tuple[int, int]:
    """Find the closest raw brace block around an anchor, within a local radius."""

    lower = max(1, anchor - DEFAULT_RADIUS)
    upper = min(len(lines), anchor + DEFAULT_RADIUS)
    depth = 0
    opening_line = None

    for number in range(anchor, lower - 1, -1):
        for char in reversed(lines[number - 1]):
            if char == "}":
                depth += 1
            elif char == "{":
                if depth == 0:
                    opening_line = number
                    break
                depth -= 1
        if opening_line is not None:
            break

    if opening_line is None:
        return lower, upper

    depth = 0
    for number in range(opening_line, upper + 1):
        for char in lines[number - 1]:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return opening_line, number
    return opening_line, upper


def _scan_scope(
    lines: list[str], start_line: int, end_line: int
) -> dict[str, Any] | None:
    state = "normal"
    string_start = 0
    block_comment_start = 0
    brace_stack: list[int] = []

    for line_number in range(start_line, end_line + 1):
        line = lines[line_number - 1]
        index = 0
        while index < len(line):
            char = line[index]
            next_char = line[index + 1] if index + 1 < len(line) else ""

            if state == "line_comment":
                break
            if state == "block_comment":
                if char == "*" and next_char == "/":
                    state = "normal"
                    index += 2
                else:
                    index += 1
                continue
            if state == "char":
                if char == "\\":
                    index += 2
                elif char == "'":
                    state = "normal"
                    index += 1
                else:
                    index += 1
                continue
            if state == "regular_string":
                if char == "\\":
                    index += 2
                elif char == '"':
                    state = "normal"
                    index += 1
                else:
                    index += 1
                continue
            if state == "verbatim_string":
                if char != '"':
                    index += 1
                    continue
                if next_char == '"':
                    index += 2
                    continue
                if _is_suspicious_verbatim_quote(line, index):
                    return _candidate(
                        line_number,
                        "unescaped_quote_in_verbatim_string",
                        line,
                    )
                state = "normal"
                index += 1
                continue

            if char == "/" and next_char == "/":
                state = "line_comment"
                break
            if char == "/" and next_char == "*":
                state = "block_comment"
                block_comment_start = line_number
                index += 2
                continue
            if char == "'":
                state = "char"
                string_start = line_number
                index += 1
                continue
            if char == "@" and next_char == '"':
                state = "verbatim_string"
                string_start = line_number
                index += 2
                continue
            if char == '"':
                state = "regular_string"
                string_start = line_number
                index += 1
                continue
            if char == "{":
                brace_stack.append(line_number)
            elif char == "}":
                if brace_stack:
                    brace_stack.pop()
                else:
                    return _candidate(line_number, "unexpected_closing_block", line)
            index += 1

        if state == "line_comment":
            state = "normal"
        elif state in {"regular_string", "char"}:
            rule = (
                "unclosed_string"
                if state == "regular_string"
                else "unclosed_character_literal"
            )
            return _candidate(string_start, rule, lines[string_start - 1])

    scope_reaches_file_end = end_line == len(lines)
    if state == "verbatim_string" and scope_reaches_file_end:
        return _candidate(
            string_start,
            "unclosed_verbatim_string",
            lines[string_start - 1],
        )
    if state == "block_comment" and scope_reaches_file_end:
        return _candidate(
            block_comment_start,
            "unclosed_block_comment",
            lines[block_comment_start - 1],
        )
    if brace_stack and scope_reaches_file_end:
        line_number = brace_stack[-1]
        return _candidate(line_number, "unclosed_block", lines[line_number - 1])
    return None


def _is_suspicious_verbatim_quote(line: str, quote_index: int) -> bool:
    """Identify a likely embedded quote that prematurely ends a verbatim string."""

    remainder = line[quote_index + 1 :]
    stripped = remainder.lstrip()
    if not stripped.startswith("/"):
        return False

    # A slash immediately after the apparent close, followed by another quote,
    # is characteristic of embedded JavaScript regex such as replace(/"/g, ...).
    position = quote_index + 1
    while position < len(line):
        if line[position] == '"':
            if position + 1 < len(line) and line[position + 1] == '"':
                position += 2
                continue
            return True
        position += 1
    return False


def _candidate(line: int, rule: str, source_line: str) -> dict[str, Any]:
    evidence = source_line.strip()
    if len(evidence) > 160:
        evidence = evidence[:157] + "..."
    return {"line": line, "rule": rule, "evidence": evidence}


def _recommendation(rule: str) -> str:
    actions = {
        "unescaped_quote_in_verbatim_string": (
            'Escape literal double quotes inside the C# verbatim string as "".'
        ),
        "unclosed_verbatim_string": (
            "Add the missing closing double quote to the verbatim string."
        ),
        "unclosed_string": "Add the missing closing double quote to the string.",
        "unclosed_character_literal": "Add the missing closing quote to the character literal.",
        "unclosed_block": "Add the missing closing brace for the indicated block.",
        "unexpected_closing_block": "Remove or match the unexpected closing brace.",
        "unclosed_block_comment": "Add the missing */ terminator to the block comment.",
    }
    return actions.get(rule, "Review the indicated structural delimiter.")


def _result(
    *,
    status: str,
    scope: tuple[int, int],
    candidate: dict[str, Any] | None,
    recommended_action: str,
    escalated: bool,
    escalation_reason: str | None,
    anchor_source: str | None = None,
) -> dict[str, Any]:
    start, end = scope
    result: dict[str, Any] = {
        "status": status,
        "language": "csharp",
        "strategy": STRATEGY,
        "scope": {"start_line": start, "end_line": end},
        "candidate": candidate,
        "lines_analyzed": end - start + 1 if start and end else 0,
        "escalated": escalated,
        "recommended_action": recommended_action,
    }
    if anchor_source is not None:
        result["anchor_source"] = anchor_source
    if escalation_reason is not None:
        result["escalation_reason"] = escalation_reason
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local C# structure.")
    parser.add_argument("path", help="Path to a C# source file")
    parser.add_argument(
        "--line",
        type=int,
        dest="error_line",
        help="Optional line reported by the C# compiler",
    )
    args = parser.parse_args(argv)
    result = analyze_file(args.path, error_line=args.error_line)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
