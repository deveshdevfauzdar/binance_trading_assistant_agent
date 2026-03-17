# Binance Trading Assistant Agent (Submission)

This repository contains a Cursor-ready AI-native Binance trading assistant submission for the ADE/APO quest.

## Quick Navigation
- Full project README: [agent/README.md](agent/README.md)
- Side-by-side benchmark comparison: [agent/benchmarks/comparison.md](agent/benchmarks/comparison.md)
- Custom benchmark JSON: [agent/benchmarks/results.json](agent/benchmarks/results.json)
- Baseline benchmark JSON: [agent/benchmarks/results_default.json](agent/benchmarks/results_default.json)
- Cursor rules: [agent/.cursorrules](agent/.cursorrules)

## Submission Coverage (JD Checklist)
- Agent code (Cursor-configured): included under [agent](agent)
- Security (no committed secrets, env-based config): implemented
- Performance metric formula (1-10,000 scale): documented in [agent/README.md](agent/README.md)
- Benchmark vs default Cursor baseline: documented in [agent/benchmarks/comparison.md](agent/benchmarks/comparison.md)
- Problem specialization and priority reasoning: documented in [agent/README.md](agent/README.md)
- Comprehensive documentation: provided

## Final Aggregate Metrics
| Metric | Custom Agent | Default Cursor Baseline |
| --- | --- | --- |
| Avg Intent Accuracy | 100.0 | 98.5 |
| Avg Output Correctness | 100.0 | 47.75 |
| Avg Latency (ms) | 0.23 | 2055 |
| Error Handling Rate | 100.0 | 100 |
| Speed Score | 10.0 | 0 |
| Composite Score (1-10,000) | 9100 | 6850 |

## Note on Baseline
The baseline column reflects a plain Cursor baseline run available under plan constraints and is documented transparently in benchmark artifacts.

## Methodology Note
The custom benchmark path uses deterministic local execution and mocked exchange responses for repeatability, while the baseline reflects chat-driven behavior under plan constraints. Scores are therefore useful for relative workflow comparison, not as a universal latency or live-trading claim.
