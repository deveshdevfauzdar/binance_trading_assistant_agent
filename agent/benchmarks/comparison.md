# Benchmark Comparison: Custom Agent vs Default Claude

| Test Case | Custom Agent Result | Default Claude Result | Winner |
| --- | --- | --- | --- |
| 1. accumulate eth slowly near 2800 | intent=100.0, output=100.0, latency=0.28ms | intent=100, output=100, latency=1600ms | Tie |
| 2. buy eth at 3000 with 0.05 | intent=100.0, output=100.0, latency=0.49ms | intent=100, output=100, latency=1500ms | Tie |
| 3. buy if market vibes are good | intent=100.0, output=100.0, latency=0.01ms | intent=100, output=70, latency=1100ms | Custom |
| 4. can you get my open orders for eth? | intent=100.0, output=100.0, latency=0.02ms | intent=100, output=10, latency=3000ms | Custom |
| 5. check if i have any open orders | intent=100.0, output=100.0, latency=0.03ms | intent=100, output=10, latency=2800ms | Custom |
| 6. do i still have pending orders | intent=100.0, output=100.0, latency=0.02ms | intent=100, output=10, latency=2600ms | Custom |
| 7. execute magic alpha strategy | intent=100.0, output=100.0, latency=0.01ms | intent=100, output=70, latency=1200ms | Custom |
| 8. get my open orders | intent=100.0, output=100.0, latency=0.3ms | intent=70, output=10, latency=3500ms | Custom |
| 9. get my open orders for BTCUSDT | intent=100.0, output=100.0, latency=0.05ms | intent=100, output=10, latency=3200ms | Custom |
| 10. i want to place a buy limit for ada at 0.75 | intent=100.0, output=100.0, latency=0.28ms | intent=100, output=90, latency=1700ms | Custom |
| 11. place limit buy order for BTCUSDT at 61000 qty 0.002 | intent=100.0, output=100.0, latency=0.04ms | intent=100, output=100, latency=1300ms | Tie |
| 12. place limit buy order for ETH at 3200 quantity 0.1 | intent=100.0, output=100.0, latency=0.43ms | intent=100, output=100, latency=1400ms | Tie |
| 13. place order | intent=100.0, output=100.0, latency=0.01ms | intent=100, output=70, latency=900ms | Custom |
| 14. please show me the current price of bnb | intent=100.0, output=100.0, latency=0.02ms | intent=100, output=30, latency=2100ms | Custom |
| 15. set a bid for sol at 145, use 1 coin | intent=100.0, output=100.0, latency=0.4ms | intent=100, output=20, latency=2300ms | Custom |
| 16. show BTC price | intent=100.0, output=100.0, latency=2.08ms | intent=100, output=30, latency=2600ms | Custom |
| 17. show ETH price | intent=100.0, output=100.0, latency=0.11ms | intent=100, output=30, latency=2400ms | Custom |
| 18. show SOL price | intent=100.0, output=100.0, latency=0.03ms | intent=100, output=30, latency=2200ms | Custom |
| 19. show doge | intent=100.0, output=100.0, latency=0.02ms | intent=100, output=30, latency=1800ms | Custom |
| 20. what is btc trading at right now | intent=100.0, output=100.0, latency=0.02ms | intent=100, output=35, latency=1900ms | Custom |

## Aggregate Metrics

| Metric | Custom Agent | Default Claude Result |
| --- | --- | --- |
| Avg Intent Accuracy | 100.0 | 98.5 |
| Avg Output Correctness | 100.0 | 47.75 |
| Avg Latency (ms) | 0.23 | 2055 |
| Error Handling Rate | 100.0 | 100 |
| Speed Score | 10.0 | 0 |
| Composite Score (1-10,000) | 9100 | 6850 |

## Summary

### Where the custom agent should win
- Domain-specific accuracy: Binance-oriented intent patterns and symbol normalization improve command handling.
- Structured output: predictable, machine-friendly responses are easier to benchmark and automate.
- Security enforcement: env-based secret management and project rules reduce credential exposure risk.

### Where default Claude may still be stronger
- General knowledge breadth: broader performance on non-trading and open-ended prompts.

### Notes
- If a result is missing, the table keeps `TBD` placeholders until that benchmark run is provided.
- Winner is computed from (intent_accuracy + output_correctness) as a simple placeholder heuristic.
