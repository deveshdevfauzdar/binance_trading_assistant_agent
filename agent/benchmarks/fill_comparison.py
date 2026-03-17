from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_results(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def case_map(data: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not data:
        return {}
    mapped: dict[str, dict[str, Any]] = {}
    for case in data.get("cases", []):
        mapped[str(case.get("command", ""))] = case
    return mapped


def format_result(case: dict[str, Any] | None) -> str:
    if not case:
        return "TBD (intent: __, output: __, latency: __ms)"
    intent = case.get("intent_accuracy", "__")
    output = case.get("output_correctness", "__")
    latency = case.get("latency_ms", "__")
    return f"intent={intent}, output={output}, latency={latency}ms"


def pick_winner(custom_case: dict[str, Any] | None, default_case: dict[str, Any] | None) -> str:
    if not custom_case or not default_case:
        return "TBD"
    c_score = float(custom_case.get("intent_accuracy", 0)) + float(custom_case.get("output_correctness", 0))
    d_score = float(default_case.get("intent_accuracy", 0)) + float(default_case.get("output_correctness", 0))
    if c_score > d_score:
        return "Custom"
    if d_score > c_score:
        return "Default"
    return "Tie"


def build_markdown(custom_data: dict[str, Any] | None, default_data: dict[str, Any] | None) -> str:
    custom_cases = case_map(custom_data)
    default_cases = case_map(default_data)
    commands = sorted(set(custom_cases) | set(default_cases))
    lines = [
        "# Benchmark Comparison: Custom Agent vs Default Claude",
        "",
        "| Test Case | Custom Agent Result | Default Claude Result | Winner |",
        "| --- | --- | --- | --- |",
    ]
    for index, command in enumerate(commands, start=1):
        c_case = custom_cases.get(command)
        d_case = default_cases.get(command)
        winner = pick_winner(c_case, d_case)
        lines.append(f"| {index}. {command} | {format_result(c_case)} | {format_result(d_case)} | {winner} |")

    c_summary = (custom_data or {}).get("summary", {})
    d_summary = (default_data or {}).get("summary", {})

    lines.extend(
        [
            "",
            "## Aggregate Metrics",
            "",
            "| Metric | Custom Agent | Default Claude Result |",
            "| --- | --- | --- |",
            f"| Avg Intent Accuracy | {c_summary.get('avg_intent_accuracy', 'TBD')} | {d_summary.get('avg_intent_accuracy', 'TBD')} |",
            f"| Avg Output Correctness | {c_summary.get('avg_output_correctness', 'TBD')} | {d_summary.get('avg_output_correctness', 'TBD')} |",
            f"| Avg Latency (ms) | {c_summary.get('avg_latency_ms', 'TBD')} | {d_summary.get('avg_latency_ms', 'TBD')} |",
            f"| Error Handling Rate | {c_summary.get('error_handling_rate', 'TBD')} | {d_summary.get('error_handling_rate', 'TBD')} |",
            f"| Speed Score | {c_summary.get('speed_score', 'TBD')} | {d_summary.get('speed_score', 'TBD')} |",
            f"| Composite Score (1-10,000) | {c_summary.get('composite_score_1_to_10000', 'TBD')} | {d_summary.get('composite_score_1_to_10000', 'TBD')} |",
        ]
    )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "### Where the custom agent should win",
            "- Domain-specific accuracy: Binance-oriented intent patterns and symbol normalization improve command handling.",
            "- Structured output: predictable, machine-friendly responses are easier to benchmark and automate.",
            "- Security enforcement: env-based secret management and project rules reduce credential exposure risk.",
            "",
            "### Where default Claude may still be stronger",
            "- General knowledge breadth: broader performance on non-trading and open-ended prompts.",
            "",
            "### Notes",
            "- If a result is missing, the table keeps `TBD` placeholders until that benchmark run is provided.",
            "- Winner is computed from (intent_accuracy + output_correctness) as a simple placeholder heuristic.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-fill benchmark comparison markdown.")
    parser.add_argument("--custom", default="benchmarks/results.json", help="Path to custom-agent results JSON")
    parser.add_argument("--default", default="benchmarks/results_default.json", help="Path to default-Claude results JSON")
    parser.add_argument("--out", default="benchmarks/comparison.md", help="Output markdown path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    custom = load_results(root / args.custom)
    default = load_results(root / args.default)
    content = build_markdown(custom, default)
    out_path = root / args.out
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote comparison to: {out_path}")


if __name__ == "__main__":
    main()