from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from agent import AssistantSettings, TradingAssistantAgent
from binance_client import BinanceClientWrapper, BinanceConfig
from claude_intent_parser import ClaudeIntentParser
from router import CommandRouter


def _as_bool(value: str, default: bool) -> bool:
    text = (value or "").strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def build_agent() -> TradingAssistantAgent:
    load_dotenv()

    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    if not api_key or not api_secret:
        raise RuntimeError("Missing BINANCE_API_KEY or BINANCE_API_SECRET in .env")

    config = BinanceConfig(
        api_key=api_key,
        api_secret=api_secret,
        testnet=_as_bool(os.getenv("BINANCE_TESTNET", "true"), True),
        recv_window=int(os.getenv("BINANCE_RECV_WINDOW", "5000")),
        dry_run=_as_bool(os.getenv("BINANCE_DRY_RUN", "true"), True),
        default_quote_asset=os.getenv("DEFAULT_QUOTE_ASSET", "USDT").upper(),
    )

    settings = AssistantSettings(default_order_qty=os.getenv("DEFAULT_ORDER_QTY", "0.001"))
    base_dir = Path(__file__).resolve().parent
    claude_parser = ClaudeIntentParser(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        prompt_path=str(base_dir / "system_prompt.txt"),
    )

    return TradingAssistantAgent(
        binance_client=BinanceClientWrapper(config),
        router=CommandRouter(),
        settings=settings,
        claude_parser=claude_parser,
    )


def main() -> None:
    assistant = build_agent()
    print("Binance Trading Assistant")
    print("Type 'help' for commands. Type 'exit' to quit.")

    while True:
        user_input = input("\n> ")
        response = assistant.handle(user_input)
        if response == "exit":
            print("Goodbye.")
            break
        print(response)


if __name__ == "__main__":
    main()