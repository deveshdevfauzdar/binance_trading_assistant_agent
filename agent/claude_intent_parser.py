from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from anthropic import Anthropic


@dataclass(frozen=True)
class ParsedIntent:
    action: str
    symbol: str | None
    quantity: float | None
    price: float | None


class ClaudeIntentParser:
    def __init__(self, api_key: str, model: str, prompt_path: str) -> None:
        self._api_key = api_key.strip()
        self._model = model.strip()
        self._system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        self._client = Anthropic(api_key=self._api_key) if self._api_key else None

    def is_enabled(self) -> bool:
        return self._client is not None

    def parse(self, user_input: str) -> tuple[ParsedIntent | None, str | None]:
        if self._client is None:
            return None, "Claude parser unavailable: missing ANTHROPIC_API_KEY"

        try:
            # Streaming gives lower latency and returns full text when the stream completes.
            with self._client.messages.stream(
                model=self._model,
                max_tokens=180,
                system=self._system_prompt,
                messages=[{"role": "user", "content": user_input}],
                temperature=0.0,
            ) as stream:
                chunks: list[str] = []
                for text in stream.text_stream:
                    chunks.append(text)
                raw = "".join(chunks).strip()

            parsed = self._safe_json_to_intent(raw)
            if parsed is None:
                return None, "Claude parser returned invalid JSON"
            return parsed, None
        except Exception as exc:
            return None, self._safe_error(exc)

    @staticmethod
    def _safe_error(exc: Exception) -> str:
        redacted = re.sub(r"(?i)(api[_-]?key|secret|token|password)=([^&\s]+)", r"\1=<redacted>", str(exc))
        return f"Claude parser failed: {type(exc).__name__} ({redacted[:180]})"

    def _safe_json_to_intent(self, raw: str) -> ParsedIntent | None:
        payload = self._extract_json(raw)
        if payload is None:
            return None

        action = str(payload.get("action", "unknown")).strip().lower()
        symbol_raw = payload.get("symbol")
        symbol = str(symbol_raw).strip().upper() if symbol_raw is not None else None
        quantity = self._as_float(payload.get("quantity"))
        price = self._as_float(payload.get("price"))

        return ParsedIntent(action=action, symbol=symbol, quantity=quantity, price=price)

    @staticmethod
    def _as_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any] | None:
        raw = raw.strip()
        if not raw:
            return None

        try:
            candidate = json.loads(raw)
            return candidate if isinstance(candidate, dict) else None
        except json.JSONDecodeError:
            pass

        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        try:
            candidate = json.loads(raw[start : end + 1])
            return candidate if isinstance(candidate, dict) else None
        except json.JSONDecodeError:
            return None
