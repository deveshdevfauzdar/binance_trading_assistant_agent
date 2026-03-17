from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RouteResult:
    intent: str
    symbol: Optional[str] = None
    price: Optional[str] = None
    quantity: Optional[str] = None


class CommandRouter:
    def route(self, user_input: str) -> RouteResult:
        lowered = user_input.strip().lower()
        if lowered in {"exit", "quit", "q"}:
            return RouteResult(intent="exit")
        if lowered in {"help", "h", "?"}:
            return RouteResult(intent="help")

        show_price = self._parse_show_price(lowered)
        if show_price is not None:
            return show_price

        open_orders = self._parse_open_orders(lowered)
        if open_orders is not None:
            return open_orders

        buy_order = self._parse_limit_buy(lowered)
        if buy_order is not None:
            return buy_order

        return RouteResult(intent="unknown")

    def _parse_show_price(self, lowered: str) -> RouteResult | None:
        patterns = [
            r"show\s+me\s+the\s+current\s+price\s+of\s+([a-z]{2,10})",
            r"what\s+is\s+([a-z]{2,10})\s+trading\s+at",
            r"price\s+of\s+([a-z]{2,10})",
            r"\bshow\s+([a-z]{2,10})(?:\s+price)?\b",
        ]
        symbol = self._first_group_match(patterns, lowered)
        if symbol:
            return RouteResult(intent="show_price", symbol=symbol)
        return None

    def _parse_open_orders(self, lowered: str) -> RouteResult | None:
        symbol_match = re.search(r"open\s+orders(?:\s+for\s+([a-z]{2,15}))?", lowered)
        has_open_orders_phrase = any(
            phrase in lowered
            for phrase in ["open orders", "pending orders", "any orders", "my orders"]
        )
        if symbol_match or has_open_orders_phrase:
            symbol = self._sanitize_symbol(symbol_match.group(1)) if symbol_match else None
            return RouteResult(intent="get_open_orders", symbol=symbol)
        return None

    def _parse_limit_buy(self, lowered: str) -> RouteResult | None:
        strict_match = re.search(
            (
                r"place\s+limit\s+buy\s+order\s+for\s+([a-z]{2,15})\s+at\s+([0-9]*\.?[0-9]+)"
                r"(?:\s+(?:qty|quantity)\s+([0-9]*\.?[0-9]+))?"
            ),
            lowered,
        )
        if strict_match:
            return RouteResult(
                intent="place_limit_buy",
                symbol=self._sanitize_symbol(strict_match.group(1)),
                price=strict_match.group(2),
                quantity=strict_match.group(3),
            )

        relaxed_patterns = [
            r"buy\s+([a-z]{2,15})\s+at\s+([0-9]*\.?[0-9]+)(?:\s+with\s+([0-9]*\.?[0-9]+))?",
            r"buy\s+limit\s+for\s+([a-z]{2,15})\s+at\s+([0-9]*\.?[0-9]+)",
            r"accumulate\s+([a-z]{2,15}).*?(?:near|at)\s+([0-9]*\.?[0-9]+)",
            r"set\s+a\s+bid\s+for\s+([a-z]{2,15})\s+at\s+([0-9]*\.?[0-9]+)(?:,?\s+use\s+([0-9]*\.?[0-9]+))?",
        ]
        for pattern in relaxed_patterns:
            match = re.search(pattern, lowered)
            if match:
                return RouteResult(
                    intent="place_limit_buy",
                    symbol=self._sanitize_symbol(match.group(1)),
                    price=match.group(2),
                    quantity=match.group(3) if match.lastindex and match.lastindex >= 3 else None,
                )
        return None

    def _first_group_match(self, patterns: list[str], text: str) -> str | None:
        skip_tokens = {"me", "my", "the", "current", "price", "open", "orders"}
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                token = self._sanitize_symbol(match.group(1))
                if token and token.lower() not in skip_tokens:
                    return token
        return None

    def _sanitize_symbol(self, raw: str | None) -> str | None:
        if raw is None:
            return None
        cleaned = re.sub(r"[^a-zA-Z]", "", raw).upper()
        return cleaned or None