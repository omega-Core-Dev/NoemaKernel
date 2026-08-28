"""Noema intent hook and privacy-preserving token telemetry.

Uses only the Python standard library. Token estimates are a stable comparison
proxy, not a model tokenizer and not a substitute for provider usage metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "0.1"
ESTIMATOR = "utf8-bytes-div-4-v1"
TELEMETRY_VALUES = {"1", "true", "yes", "on", "local"}
EXPERIMENT_MODES = {"baseline", "assisted"}
CONSTRAINT_MARKERS = (
    "não ", "nao ", "sem ", "deve ", "must ", "do not ", "never ",
    "apenas ", "somente ", "restri", "limite", "proib",
)
ACCEPTANCE_MARKERS = (
    "teste", "test ", "valid", "aceita", "critério", "criterio", "saída",
    "saida", "resultado", "ao terminar", "done", "success",
)
DELIVERABLE_MARKERS = (
    "implementar", "criar", "adicionar", "alterar", "entregar", "build ",
    "implement ", "create ", "add ", "output ", "deliver",
)


def estimate_tokens(text: str) -> int:
    """Return a deterministic, explicitly approximate token estimate."""

    if not text:
        return 0
    return max(1, math.ceil(len(text.encode("utf-8")) / 4))


def structure_intent(prompt: str) -> dict[str, Any]:
    """Extract a compact, evidence-linked intent contract from a prompt."""

    segments = _prompt_segments(prompt)
    goal = _clip(segments[0] if segments else "", 240)
    constraints = _matching_lines(segments, CONSTRAINT_MARKERS)
    acceptance = _matching_lines(segments, ACCEPTANCE_MARKERS)
    deliverables = _matching_lines(segments, DELIVERABLE_MARKERS)
    code_signals = sorted(
        set(
            re.findall(
                r"\b[\w.-]+\.(?:py|cs|js|ts|json|md|toml|ya?ml)\b",
                prompt,
                re.I,
            )
        )
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "goal": goal,
        "deliverables": deliverables[:8],
        "constraints": constraints[:10],
        "acceptance": acceptance[:8],
        "authority": {"original": "authoritative", "packet": "advisory"},
    }
    if code_signals:
        packet["artifacts_mentioned"] = code_signals[:12]
    return packet


def should_structure(prompt: str, packet: dict[str, Any] | None = None) -> bool:
    packet = packet or structure_intent(prompt)
    if estimate_tokens(prompt) < 100:
        return False
    signals = (
        len(prompt) >= 240,
        len(prompt.splitlines()) >= 5,
        bool(packet["constraints"]),
        bool(packet["acceptance"]),
        len(packet["deliverables"]) >= 2,
    )
    return sum(signals) >= 2


def intent_context(packet: dict[str, Any]) -> str:
    return "NOEMA_INTENT_PACKET\n" + json.dumps(
        packet, ensure_ascii=False, separators=(",", ":")
    )


def compare_prompt_cost(prompt: str) -> dict[str, Any]:
    packet = structure_intent(prompt)
    context = intent_context(packet) if should_structure(prompt, packet) else ""
    baseline = estimate_tokens(prompt)
    contract = estimate_tokens(context)
    assisted = baseline + contract
    return {
        "measurement": "estimated_prompt_only",
        "estimator": ESTIMATOR,
        "baseline_tokens": baseline,
        "contract_tokens": contract,
        "assisted_tokens": assisted,
        "delta_tokens": assisted - baseline,
        "net_savings_tokens": baseline - assisted,
        "delta_percent": round(((assisted - baseline) / baseline * 100), 2)
        if baseline
        else 0.0,
        "structured": bool(context),
    }


def compare_actual(
    baseline_input: int,
    baseline_output: int,
    assisted_input: int,
    assisted_output: int,
) -> dict[str, Any]:
    baseline = baseline_input + baseline_output
    assisted = assisted_input + assisted_output
    delta = assisted - baseline
    return {
        "measurement": "actual_usage_supplied_by_user",
        "baseline": {
            "input_tokens": baseline_input,
            "output_tokens": baseline_output,
            "total_tokens": baseline,
        },
        "assisted": {
            "input_tokens": assisted_input,
            "output_tokens": assisted_output,
            "total_tokens": assisted,
        },
        "delta_tokens": delta,
        "net_savings_tokens": -delta,
        "net_savings_percent": round((-delta / baseline * 100), 2)
        if baseline
        else 0.0,
    }


def handle_hook(payload: dict[str, Any]) -> dict[str, Any]:
    event = payload.get("hook_event_name", "unknown")
    telemetry: dict[str, Any] = _base_event(payload)

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt", ""))
        packet = structure_intent(prompt)
        context = intent_context(packet) if should_structure(prompt, packet) else ""
        mode = experiment_mode()
        comparison = compare_prompt_cost(prompt)
        injected = bool(context) and mode == "assisted"
        telemetry.update(
            {
                "kind": "prompt",
                **comparison,
                "injected": injected,
                "observed_prompt_tokens": (
                    comparison["assisted_tokens"]
                    if injected
                    else comparison["baseline_tokens"]
                ),
            }
        )
        _write_telemetry(telemetry)
        if not injected:
            return {}
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }

    if event == "PostToolUse":
        telemetry.update(
            {
                "kind": "tool",
                "tool_name": str(payload.get("tool_name", "unknown")),
                "tool_input_chars": len(json.dumps(payload.get("tool_input", {}))),
                "tool_response_chars": len(json.dumps(payload.get("tool_response", {}))),
            }
        )
        _write_telemetry(telemetry)
        return {}

    if event == "Stop":
        response = str(payload.get("last_assistant_message", ""))
        telemetry.update(
            {
                "kind": "stop",
                "response_chars": len(response),
                "response_estimated_tokens": estimate_tokens(response),
            }
        )
        _write_telemetry(telemetry)
        return {}

    telemetry["kind"] = "lifecycle"
    _write_telemetry(telemetry)
    return {}


def summarize_events(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(events)
    prompts = [event for event in items if event.get("kind") == "prompt"]
    tools = [event for event in items if event.get("kind") == "tool"]
    stops = [event for event in items if event.get("kind") == "stop"]
    sessions = {
        event.get("session_hash") for event in items if event.get("session_hash")
    }
    baseline = sum(int(event.get("baseline_tokens", 0)) for event in prompts)
    assisted = sum(int(event.get("assisted_tokens", 0)) for event in prompts)
    by_mode = {
        mode: _summarize_mode(items, mode) for mode in sorted(EXPERIMENT_MODES)
    }
    baseline_total = by_mode["baseline"]["estimated_total_tokens"]
    assisted_total = by_mode["assisted"]["estimated_total_tokens"]
    has_comparison = bool(
        by_mode["baseline"]["completed_turns"]
        and by_mode["assisted"]["completed_turns"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "privacy": "no_prompt_or_source_content_stored",
        "measurement": "estimated_unless_actual_usage_is_supplied_separately",
        "estimator": ESTIMATOR,
        "sessions": len(sessions),
        "prompt_events": len(prompts),
        "structured_prompts": sum(bool(event.get("structured")) for event in prompts),
        "tool_calls": len(tools),
        "completed_turns": len(stops),
        "baseline_prompt_tokens": baseline,
        "assisted_prompt_tokens": assisted,
        "delta_prompt_tokens": assisted - baseline,
        "net_prompt_savings_tokens": baseline - assisted,
        "estimated_response_tokens": sum(
            int(event.get("response_estimated_tokens", 0)) for event in stops
        ),
        "by_mode": by_mode,
        "ab_comparison_available": has_comparison,
        "estimated_task_delta_tokens": (
            assisted_total - baseline_total if has_comparison else None
        ),
        "estimated_task_net_savings_tokens": (
            baseline_total - assisted_total if has_comparison else None
        ),
    }


def _summarize_mode(events: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    selected = [event for event in events if event.get("mode") == mode]
    prompts = [event for event in selected if event.get("kind") == "prompt"]
    stops = [event for event in selected if event.get("kind") == "stop"]
    prompt_tokens = sum(
        int(event.get("observed_prompt_tokens", 0)) for event in prompts
    )
    response_tokens = sum(
        int(event.get("response_estimated_tokens", 0)) for event in stops
    )
    return {
        "sessions": len(
            {event.get("session_hash") for event in selected if event.get("session_hash")}
        ),
        "prompt_events": len(prompts),
        "tool_calls": sum(event.get("kind") == "tool" for event in selected),
        "completed_turns": len(stops),
        "estimated_prompt_tokens": prompt_tokens,
        "estimated_response_tokens": response_tokens,
        "estimated_total_tokens": prompt_tokens + response_tokens,
    }


def _matching_lines(lines: list[str], markers: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for line in lines:
        lowered = line.lower()
        if any(marker in lowered for marker in markers):
            clipped = _clip(line, 220)
            if clipped not in matches:
                matches.append(clipped)
    return matches


def _prompt_segments(prompt: str) -> list[str]:
    segments: list[str] = []
    for raw_line in prompt.splitlines():
        line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw_line).strip()
        if not line:
            continue
        for part in re.split(r"(?<=[.!?])\s+|;\s*", line):
            cleaned = part.strip().rstrip(".")
            if cleaned:
                segments.append(cleaned)
    return segments


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _hash_identifier(value: Any) -> str | None:
    if not value:
        return None
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _base_event(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": str(payload.get("hook_event_name", "unknown")),
        "session_hash": _hash_identifier(payload.get("session_id")),
        "turn_hash": _hash_identifier(payload.get("turn_id")),
        "model": str(payload.get("model", "unknown")),
        "mode": experiment_mode(),
    }


def _telemetry_enabled() -> bool:
    return os.environ.get("NOEMA_TELEMETRY", "").lower() in TELEMETRY_VALUES


def experiment_mode() -> str:
    mode = os.environ.get("NOEMA_EXPERIMENT_MODE", "assisted").lower()
    return mode if mode in EXPERIMENT_MODES else "assisted"


def telemetry_path() -> Path:
    data_root = os.environ.get("PLUGIN_DATA")
    if data_root:
        return Path(data_root, "noema-telemetry.jsonl")
    return Path.cwd() / ".noema" / "telemetry.jsonl"


def _write_telemetry(event: dict[str, Any]) -> None:
    if not _telemetry_enabled():
        return
    path = telemetry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(
            json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"
        )


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                events.append(json.loads(line))
    return events


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Noema intent runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("hook", help="Process one Codex hook event from stdin")

    analyze = subparsers.add_parser("analyze", help="Structure and estimate one prompt")
    analyze.add_argument("--prompt-file", type=Path)
    analyze.add_argument("--text")

    actual = subparsers.add_parser("compare-actual", help="Subtract observed A/B usage")
    actual.add_argument("--baseline-input", type=int, required=True)
    actual.add_argument("--baseline-output", type=int, required=True)
    actual.add_argument("--assisted-input", type=int, required=True)
    actual.add_argument("--assisted-output", type=int, required=True)

    report = subparsers.add_parser("report", help="Summarize local telemetry")
    report.add_argument("--telemetry-file", type=Path)

    args = parser.parse_args(argv)
    if args.command == "hook":
        payload = json.load(sys.stdin)
        print(json.dumps(handle_hook(payload), ensure_ascii=False))
        return 0
    if args.command == "analyze":
        if bool(args.prompt_file) == bool(args.text):
            parser.error("provide exactly one of --prompt-file or --text")
        prompt = (
            args.prompt_file.read_text(encoding="utf-8")
            if args.prompt_file
            else args.text
        )
        result = {
            "intent_packet": structure_intent(prompt),
            "comparison": compare_prompt_cost(prompt),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "compare-actual":
        result = compare_actual(
            args.baseline_input,
            args.baseline_output,
            args.assisted_input,
            args.assisted_output,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    path = args.telemetry_file or telemetry_path()
    print(
        json.dumps(
            summarize_events(load_events(path)), ensure_ascii=False, indent=2
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
