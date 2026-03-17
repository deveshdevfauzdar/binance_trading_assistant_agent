from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: int
    difficulty: str
    command: str
    expected_action: str
    expected_symbol: str | None = None
    expected_quantity: float | None = None
    expected_price: float | None = None


TEST_CASES: list[BenchmarkCase] = [
    BenchmarkCase(1, "easy", "show BTC price", "show_price", "BTCUSDT"),
    BenchmarkCase(2, "easy", "show ETH price", "show_price", "ETHUSDT"),
    BenchmarkCase(3, "easy", "show SOL price", "show_price", "SOLUSDT"),
    BenchmarkCase(4, "easy", "get my open orders", "get_open_orders", None),
    BenchmarkCase(5, "easy", "get my open orders for BTCUSDT", "get_open_orders", "BTCUSDT"),
    BenchmarkCase(
        6,
        "easy",
        "place limit buy order for ETH at 3200 quantity 0.1",
        "buy",
        "ETHUSDT",
        0.1,
        3200.0,
    ),
    BenchmarkCase(
        7,
        "easy",
        "place limit buy order for BTCUSDT at 61000 qty 0.002",
        "buy",
        "BTCUSDT",
        0.002,
        61000.0,
    ),
    BenchmarkCase(8, "medium", "please show me the current price of bnb", "show_price", "BNBUSDT"),
    BenchmarkCase(9, "medium", "can you get my open orders for eth?", "get_open_orders", "ETHUSDT"),
    BenchmarkCase(10, "medium", "buy eth at 3000 with 0.05", "buy", "ETHUSDT", 0.05, 3000.0),
    BenchmarkCase(11, "medium", "i want to place a buy limit for ada at 0.75", "buy", "ADAUSDT", None, 0.75),
    BenchmarkCase(12, "medium", "check if i have any open orders", "get_open_orders", None),
    BenchmarkCase(13, "medium", "show doge", "show_price", "DOGEUSDT"),
    BenchmarkCase(14, "hard", "accumulate eth slowly near 2800", "buy", "ETHUSDT", None, 2800.0),
    BenchmarkCase(15, "hard", "what is btc trading at right now", "show_price", "BTCUSDT"),
    BenchmarkCase(16, "hard", "do i still have pending orders", "get_open_orders", None),
    BenchmarkCase(17, "hard", "set a bid for sol at 145, use 1 coin", "buy", "SOLUSDT", 1.0, 145.0),
    BenchmarkCase(18, "hard", "execute magic alpha strategy", "unknown", None),
    BenchmarkCase(19, "hard", "place order", "unknown", None),
    BenchmarkCase(20, "hard", "buy if market vibes are good", "unknown", None),
]