from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException


@dataclass(frozen=True)
class BinanceConfig:
    api_key: str
    api_secret: str
    testnet: bool = True
    recv_window: int = 5000
    dry_run: bool = True
    default_quote_asset: str = "USDT"


class BinanceClientWrapper:
    def __init__(self, config: BinanceConfig) -> None:
        self.config = config
        self.client = Client(api_key=config.api_key, api_secret=config.api_secret)
        if config.testnet:
            self.client.API_URL = "https://testnet.binance.vision/api"
        if not str(self.client.API_URL).lower().startswith("https://"):
            raise RuntimeError("Binance API URL must use HTTPS")

    def _safe_error(self, prefix: str, exc: Exception) -> dict[str, Any]:
        redacted = re.sub(r"(?i)(api[_-]?key|secret|token|password)=([^&\s]+)", r"\1=<redacted>", str(exc))
        return {"error": f"{prefix}: {type(exc).__name__}", "details": redacted[:240]}

    def normalize_symbol(self, base_asset_or_symbol: str) -> str:
        symbol = base_asset_or_symbol.upper().strip()
        if symbol.endswith(("USDT", "BUSD", "USDC", "TUSD", "FDUSD")):
            return symbol
        return f"{symbol}{self.config.default_quote_asset}"

    def get_price(self, base_asset_or_symbol: str) -> dict[str, Any]:
        symbol = self.normalize_symbol(base_asset_or_symbol)
        try:
            payload = self.client.get_symbol_ticker(symbol=symbol)
            price = Decimal(payload["price"])
            return {"symbol": symbol, "price": str(price)}
        except (BinanceAPIException, BinanceRequestException) as exc:
            return self._safe_error(f"Failed to fetch price for {symbol}", exc)

    def get_open_orders(self, symbol: Optional[str] = None) -> dict[str, Any]:
        safe_symbol = self.normalize_symbol(symbol) if symbol else None
        try:
            if safe_symbol:
                orders = self.client.get_open_orders(symbol=safe_symbol)
            else:
                orders = self.client.get_open_orders()
            return {"symbol": safe_symbol or "ALL", "orders": orders}
        except (BinanceAPIException, BinanceRequestException) as exc:
            return self._safe_error("Failed to fetch open orders", exc)

    def place_limit_buy_order(self, base_asset_or_symbol: str, price: str, quantity: str) -> dict[str, Any]:
        symbol = self.normalize_symbol(base_asset_or_symbol)
        try:
            if self.config.dry_run:
                return {
                    "dry_run": True,
                    "message": "Order not sent because BINANCE_DRY_RUN=true",
                    "order": {
                        "symbol": symbol,
                        "side": "BUY",
                        "type": "LIMIT",
                        "timeInForce": "GTC",
                        "price": str(Decimal(price)),
                        "quantity": str(Decimal(quantity)),
                    },
                }

            order = self.client.create_order(
                symbol=symbol,
                side="BUY",
                type="LIMIT",
                timeInForce="GTC",
                price=str(Decimal(price)),
                quantity=str(Decimal(quantity)),
                recvWindow=self.config.recv_window,
            )
            return {"dry_run": False, "order": order}
        except (BinanceAPIException, BinanceRequestException, ArithmeticError, ValueError) as exc:
            return self._safe_error(f"Failed to place limit buy order for {symbol}", exc)