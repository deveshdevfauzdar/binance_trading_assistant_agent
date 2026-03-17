from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent import AssistantSettings, TradingAssistantAgent
from benchmarks.test_cases import BenchmarkCase, TEST_CASES
from router import CommandRouter


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
LOGGER = logging.getLogger("benchmark_evaluator")


class MockBinanceClient:
    def get_price(self, base_asset_or_symbol: str) -> dict[str, Any]:
        symbol = self._normalize(base_asset_or_symbol)
        return {"symbol": symbol, "price": "123.45"}

    def get_open_orders(self, symbol: str | None = None) -> dict[str, Any]:
        safe_symbol = self._normalize(symbol) if symbol else "ALL"
        return {"symbol": safe_symbol, "orders": []}

    def place_limit_buy_order(self, base_asset_or_symbol: str, price: str, quantity: str) -> dict[str, Any]:
        symbol = self._normalize(base_asset_or_symbol)
        return {
            "dry_run": True,
            "order": {"symbol": symbol, "side": "BUY", "type": "LIMIT", "price": price, "quantity": quantity},
        }

    def _normalize(self, value: str | None) -> str:
        if value is None:
            return ""
        token = value.upper().strip()
        if token.endswith(("USDT", "BUSD", "USDC", "TUSD", "FDUSD")):
            return token
        return f"{token}USDT"


@dataclass
class CaseResult:
    case_id: int
    difficulty: str
    command: str
    expected_action: str
    predicted_action: str
    expected_symbol: str | None
    predicted_symbol: str | None
    intent_accuracy: float
    latency_ms: float
    error_handling_pass: bool
    output_correctness: float
    raw_response: str


def build_benchmark_agent() -> TradingAssistantAgent:
    return TradingAssistantAgent(
        binance_client=MockBinanceClient(),
        router=CommandRouter(),
        settings=AssistantSettings(default_order_qty="0.001"),
        claude_parser=None,
    )


def run_case(agent: TradingAssistantAgent, case: BenchmarkCase) -> CaseResult:
    started = time.perf_counter()
    response = agent.handle(case.command)
    latency_ms = (time.perf_counter() - started) * 1000
    predicted_action, predicted_symbol = infer_prediction(agent, case.command, response)
    intent_accuracy = score_intent(case, predicted_action, predicted_symbol, response)
    output_correctness = score_output_correctness(case, response, predicted_action, predicted_symbol)
    error_ok = is_error_handling_ok(response)
    return CaseResult(
        case_id=case.case_id,
        difficulty=case.difficulty,
        command=case.command,
        expected_action=case.expected_action,
        predicted_action=predicted_action,
        expected_symbol=case.expected_symbol,
        predicted_symbol=predicted_symbol,
        intent_accuracy=round(intent_accuracy, 2),
        latency_ms=round(latency_ms, 2),
        error_handling_pass=error_ok,
        output_correctness=round(output_correctness, 2),
        raw_response=response,
    )


def infer_prediction(agent: TradingAssistantAgent, command: str, response: str) -> tuple[str, str | None]:
    routed = agent.router.route(command)
    action_map = {"place_limit_buy": "buy", "show_price": "show_price", "get_open_orders": "get_open_orders"}
    action = action_map.get(routed.intent, routed.intent)
    symbol = normalize_symbol(routed.symbol)
    if action != "unknown":
        return action, symbol
    parsed = parse_json(response)
    if parsed is None:
        return "unknown", None
    return str(parsed.get("action", "unknown")).lower(), normalize_symbol(parsed.get("symbol"))


def score_intent(
    case: BenchmarkCase,
    predicted_action: str,
    predicted_symbol: str | None,
    response: str,
) -> float:
    score = 0.0
    if predicted_action == case.expected_action:
        score += 70
    expected_symbol = normalize_symbol(case.expected_symbol)
    if expected_symbol is None:
        score += 30
    elif predicted_symbol == expected_symbol:
        score += 30
    if predicted_action == "unknown" and case.expected_action == "unknown":
        score = max(score, 90.0 if "Unknown command" in response else score)
    return min(score, 100.0)


def score_output_correctness(
    case: BenchmarkCase,
    response: str,
    predicted_action: str,
    predicted_symbol: str | None,
) -> float:
    parsed = parse_json(response)
    score = 0.0
    if predicted_action == case.expected_action:
        score += 40
    if normalize_symbol(case.expected_symbol) == predicted_symbol:
        score += 20
    if case.expected_action == "show_price" and parsed and _is_price_payload(parsed):
        score += 20
    if case.expected_action == "get_open_orders" and parsed and _is_open_orders_payload(parsed):
        score += 20
    if case.expected_action == "buy" and parsed and _is_buy_payload(parsed):
        score += 20
    if case.expected_action == "unknown" and _is_unknown_payload(response, parsed):
        score += 20
    if _response_quality_ok(case.expected_action, response, parsed):
        score += 20
    return min(score, 100.0)


def _is_price_payload(parsed: dict[str, Any]) -> bool:
    return "symbol" in parsed and "price" in parsed


def _is_open_orders_payload(parsed: dict[str, Any]) -> bool:
    return "symbol" in parsed and "orders" in parsed and isinstance(parsed.get("orders"), list)


def _is_buy_payload(parsed: dict[str, Any]) -> bool:
    if "order" in parsed and isinstance(parsed["order"], dict):
        order = parsed["order"]
        return all(key in order for key in ("symbol", "side", "type", "price", "quantity"))
    if "execution" in parsed and isinstance(parsed["execution"], dict):
        return True
    return False


def _is_unknown_payload(response: str, parsed: dict[str, Any] | None) -> bool:
    if "Unknown command" in response:
        return True
    if parsed and str(parsed.get("action", "")).lower() == "unknown":
        return True
    return False


def _response_quality_ok(expected_action: str, response: str, parsed: dict[str, Any] | None) -> bool:
    if "traceback" in response.lower():
        return False
    if expected_action == "unknown":
        return _is_unknown_payload(response, parsed)
    if parsed is None:
        return False
    if expected_action == "show_price":
        return _is_price_payload(parsed)
    if expected_action == "get_open_orders":
        return _is_open_orders_payload(parsed)
    if expected_action == "buy":
        return _is_buy_payload(parsed)
    return False


def is_error_handling_ok(response: str) -> bool:
    blocked = ("traceback", "exception:", "keyerror", "typeerror")
    return not any(token in response.lower() for token in blocked)


def parse_json(response: str) -> dict[str, Any] | None:
    raw = response.strip()
    if not raw.startswith("{"):
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        LOGGER.exception("Failed to parse agent JSON response")
        return None


def normalize_symbol(symbol: Any) -> str | None:
    if symbol is None:
        return None
    token = str(symbol).upper().strip()
    if not token:
        return None
    if token.endswith(("USDT", "BUSD", "USDC", "TUSD", "FDUSD")):
        return token
    return f"{token}USDT"


def aggregate(case_results: list[CaseResult]) -> dict[str, Any]:
    count = len(case_results)
    avg_intent = sum(item.intent_accuracy for item in case_results) / count
    avg_output = sum(item.output_correctness for item in case_results) / count
    avg_latency = sum(item.latency_ms for item in case_results) / count
    error_rate = (sum(1 for item in case_results if item.error_handling_pass) / count) * 100
    speed_score = max(0.0, 10.0 - (avg_latency / 100.0))
    composite = (avg_intent * 40) + (avg_output * 40) + (error_rate * 10) + (speed_score * 10)
    return {
        "cases": count,
        "avg_intent_accuracy": round(avg_intent, 2),
        "avg_output_correctness": round(avg_output, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "error_handling_rate": round(error_rate, 2),
        "speed_score": round(speed_score, 2),
        "composite_score_1_to_10000": max(1, min(10000, round(composite))),
    }


def print_summary(case_results: list[CaseResult], summary: dict[str, Any]) -> None:
    header = (
        "| ID | Difficulty | Intent(0-100) | Latency(ms) | ErrorHandling | Output(0-100) |\n"
        "|----|------------|---------------|-------------|---------------|---------------|"
    )
    print("\nBenchmark Summary")
    print(header)
    for item in case_results:
        print(
            f"| {item.case_id:>2} | {item.difficulty:<10} | {item.intent_accuracy:>13.2f} "
            f"| {item.latency_ms:>11.2f} | {str(item.error_handling_pass):<13} | {item.output_correctness:>13.2f} |"
        )
    print("\nAggregate")
    for key, value in summary.items():
        print(f"- {key}: {value}")


def save_results(case_results: list[CaseResult], summary: dict[str, Any]) -> Path:
    output_path = Path(__file__).resolve().parent / "results.json"
    payload = {"summary": summary, "cases": [asdict(result) for result in case_results]}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    agent = build_benchmark_agent()
    results = [run_case(agent, case) for case in TEST_CASES]
    summary = aggregate(results)
    output_path = save_results(results, summary)
    print_summary(results, summary)
    print(f"\nSaved benchmark results to: {output_path}")


if __name__ == "__main__":
    main()