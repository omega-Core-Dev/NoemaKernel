---
name: structure-intent
description: Structure complex, multi-constraint requests into a compact intent contract and validate completion against it. Use for implementation prompts, long specifications, multi-step work, A/B token experiments, or requests with explicit deliverables, constraints, approval boundaries, and acceptance tests. Preserve the original request and treat generated fields as evidence-backed interpretations rather than replacements.
---

# Structure Intent

Use the `NOEMA_INTENT_PACKET` injected by the plugin hook as an execution index. Keep the original user request authoritative.

## Workflow

1. Read the original request and the packet.
2. Verify the packet against the original before acting. Ignore or correct any inferred field that conflicts with explicit text.
3. Use `goal`, `deliverables`, `constraints`, and `acceptance` to plan the smallest complete execution.
4. Treat any reported ambiguity as a question only when a reasonable assumption would materially change the result.
5. Preserve approval boundaries and prohibited actions.
6. Validate the final work against acceptance criteria and report evidence.

## Token experiments

For an A/B comparison, keep task, model, reasoning effort, environment, and success criteria fixed. Compare total input plus output usage, not only the first prompt. Use:

- `delta_tokens = assisted_total - baseline_total`
- `net_savings_tokens = baseline_total - assisted_total`

Positive `net_savings_tokens` means Noema used fewer tokens overall. Label the bundled estimator as approximate; prefer actual provider usage when available.

Set `NOEMA_EXPERIMENT_MODE=baseline` for the control session and `NOEMA_EXPERIMENT_MODE=assisted` for the intervention session.

## Privacy

Do not claim the telemetry stores prompts or source code. It records hashes, counts, event types, model names, and timing only. Telemetry is disabled unless `NOEMA_TELEMETRY=1` is set.

## Commands

Resolve the plugin script through `PLUGIN_ROOT` when available:

```bash
python "$PLUGIN_ROOT/scripts/noema_runtime.py" analyze --prompt-file request.txt
python "$PLUGIN_ROOT/scripts/noema_runtime.py" compare-actual \
  --baseline-input 1000 --baseline-output 400 \
  --assisted-input 850 --assisted-output 300
python "$PLUGIN_ROOT/scripts/noema_runtime.py" report
```

Never infer actual model token usage from the estimator. Supply observed input/output usage to `compare-actual` for publishable measurements.
