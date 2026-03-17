from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from binance_client import BinanceClientWrapper
from claude_intent_parser import ClaudeIntentParser, ParsedIntent
from router import CommandRouter


@dataclass
class AssistantSettings:
    default_order_qty: str = "0.001"


class TradingAssistantAgent:
    def __init__(
        self,
        binance_client: BinanceClientWrapper,
        router: CommandRouter,
        settings: AssistantSettings,
        claude_parser: ClaudeIntentParser | None = None,
    ) -> None:
        self.binance_client = binance_client
        self.router = router
        self.settings = settings
        self.claude_parser = claude_parser

    def handle(self, user_input: str) -> str:
        route = self.router.route(user_input)

        if route.intent == "help":
            return (
                "Supported commands:\n"
                "- show BTC price\n"
                "- place limit buy order for ETH at 2400 quantity 0.01\n"
                "- get my open orders\n"
                "- get my open orders for BTCUSDT\n"
                "- exit"
            )

        if route.intent == "show_price" and route.symbol:
            payload = self.binance_client.get_price(route.symbol)
            return json.dumps(payload, indent=2)

        if route.intent == "get_open_orders":
            payload = self.binance_client.get_open_orders(route.symbol)
            return json.dumps(payload, indent=2)

        if route.intent == "place_limit_buy" and route.symbol and route.price:
            qty = route.quantity or self.settings.default_order_qty
            payload = self.binance_client.place_limit_buy_order(route.symbol, route.price, qty)
            return json.dumps(payload, indent=2)

        if route.intent == "exit":
            return "exit"

        # Ambiguous or unsupported text command: try Claude intent extraction.
        parsed_response = self._handle_with_claude(user_input)
        if parsed_response is not None:
            return parsed_response

        return "Unknown command. Type 'help' to see supported commands."

    def _handle_with_claude(self, user_input: str) -> str | None:
        if self.claude_parser is None:
            return None

        parsed, error = self.claude_parser.parse(user_input)
        if error:
            return json.dumps(
                {
                    "action": "unknown",
                    "symbol": None,
                    "quantity": None,
                    "price": None,
                    "error": error,
                },
                indent=2,
            )

        if parsed is None:
            return None

        intent_payload = {
            "action": parsed.action,
            "symbol": parsed.symbol,
            "quantity": parsed.quantity,
            "price": parsed.price,
        }

        execution = self._execute_parsed_intent(parsed)
        if execution is not None:
            return json.dumps({"intent": intent_payload, "execution": execution}, indent=2)
        return json.dumps(intent_payload, indent=2)

    def _execute_parsed_intent(self, parsed: ParsedIntent) -> dict[str, Any] | None:
        action = parsed.action

        if action == "show_price" and parsed.symbol:
            return self.binance_client.get_price(parsed.symbol)

        if action == "get_open_orders":
            return self.binance_client.get_open_orders(parsed.symbol)

        if action == "buy" and parsed.symbol and parsed.price is not None:
            qty = parsed.quantity if parsed.quantity is not None else float(self.settings.default_order_qty)
            return self.binance_client.place_limit_buy_order(parsed.symbol, str(parsed.price), str(qty))

        return None