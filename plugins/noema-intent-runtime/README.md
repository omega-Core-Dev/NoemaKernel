# Noema Intent Runtime

Local Codex plugin that adds a compact intent contract to complex prompts and measures the cost of that additional context.

## Privacy

Telemetry is off by default. When enabled, it is written only to the plugin data directory and stores hashes, counts, event types, model names, and timestamps. Prompt text, source code, tool inputs, and tool outputs are not stored.

Enable it before starting Codex:

```powershell
$env:NOEMA_TELEMETRY = "1"
```

```bash
export NOEMA_TELEMETRY=1
```

Run the control session without injection:

```powershell
$env:NOEMA_EXPERIMENT_MODE = "baseline"
```

Run the equivalent session with Noema intervention:

```powershell
$env:NOEMA_EXPERIMENT_MODE = "assisted"
```

Keep the task, model, reasoning effort, environment, and acceptance criteria fixed between runs.

Review and trust the plugin hooks with `/hooks` after installation.

## Compare token usage

The automatic prompt estimate is a stable proxy, not an exact model tokenizer:

```bash
python scripts/noema_runtime.py analyze --prompt-file request.txt
```

For a publishable A/B result, run the same task with and without the plugin, keep the model and environment fixed, and supply the actual usage totals:

```bash
python scripts/noema_runtime.py compare-actual \
  --baseline-input 12000 --baseline-output 3000 \
  --assisted-input 9000 --assisted-output 2200
```

The report uses both signs:

- `delta_tokens = assisted_total - baseline_total`
- `net_savings_tokens = baseline_total - assisted_total`

Generate a local aggregate:

```bash
python scripts/noema_runtime.py report
```
