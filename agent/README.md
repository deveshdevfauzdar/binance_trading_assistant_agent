# Binance Trading Assistant Agent

This project is a production-oriented Binance workflow agent for AI-native developers. It combines deterministic command routing with Claude-based intent extraction for ambiguous language. Credentials are loaded from environment variables only, and order placement is dry-run by default.

## 1. Problem this agent solves

Manual trading operations are slow and error-prone when the workflow requires repeated intent translation, symbol normalization, and API-safe execution. This agent converts natural language commands into executable Binance actions with consistent output and predictable failure behavior. The target user is a developer who wants command-line automation that is scriptable, testable, and secure by default.

## 2. Why this is #1 priority: Priority Definition Ability

Priority Definition Ability means selecting the bottleneck that creates the largest downstream leverage, then solving it first with measurable impact. In crypto operations, the highest-leverage bottleneck is not UI polish or broad feature count; it is decision-to-execution latency under uncertainty. If intent parsing, symbol mapping, and order safety are unreliable, every higher-level feature inherits that instability. This project prioritizes the command-to-action path first because it compresses cycle time, reduces execution mistakes, and creates a stable base for later expansion (strategy modules, portfolio analytics, alerting). The priority is therefore based on compounding operational leverage, not convenience.

## 3. Setup instructions

Clone the repository, create a virtual environment, configure environment variables, install dependencies, and run the agent:

```bash
git clone <your-repo-url>
cd agent

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

copy .env.example .env
pip install -r requirements.txt
python main.py
```

Update `.env` with valid keys before live API use. Keep `BINANCE_TESTNET=true` and `BINANCE_DRY_RUN=true` until you explicitly want live order execution.

## 4. Usage examples

The agent accepts plain English commands. Expected outputs below are representative JSON shapes.

**Example 1**

Command:

```text
show BTC price
```

Expected output:

```json
{
	"symbol": "BTCUSDT",
	"price": "<current_price>"
}
```

**Example 2**

Command:

```text
get my open orders
```

Expected output:

```json
{
	"symbol": "ALL",
	"orders": []
}
```

**Example 3**

Command:

```text
get my open orders for ETH
```

Expected output:

```json
{
	"symbol": "ETHUSDT",
	"orders": []
}
```

**Example 4**

Command:

```text
place limit buy order for ETH at 3200 quantity 0.1
```

Expected output (dry-run mode):

```json
{
	"dry_run": true,
	"order": {
		"symbol": "ETHUSDT",
		"side": "BUY",
		"type": "LIMIT",
		"price": "3200",
		"quantity": "0.1"
	}
}
```

**Example 5**

Command:

```text
buy eth at 3000 with 0.05
```

Expected output:

```json
{
	"dry_run": true,
	"order": {
		"symbol": "ETHUSDT",
		"side": "BUY",
		"type": "LIMIT",
		"price": "3000",
		"quantity": "0.05"
	}
}
```

If a command is too ambiguous and cannot be safely interpreted, the response is an `unknown` action or a clear error payload.

## 5. Performance metrics

The benchmark module evaluates each test case on intent accuracy, output correctness, latency, and error handling. Composite score is computed on a 1 to 10,000 scale with this formula:

```text
score = (avg_intent_accuracy * 40)
	+ (avg_output_correctness * 40)
	+ (error_handling_rate * 10)
	+ (speed_score * 10)

speed_score = max(0, 10 - (avg_latency_ms / 100))
```

Interpretation guideline:

| Score Range | Interpretation |
| --- | --- |
| 1 - 5000 | Unstable routing and/or weak output correctness |
| 5001 - 7500 | Operationally usable, but with noticeable misses |
| 7501 - 8500 | Strong domain performance for production-oriented workflows |
| 8501 - 10000 | Excellent reliability, consistency, and speed |

## 6. Benchmark results

| Metric | Custom Agent | Default Claude (Cursor) |
| --- | --- | --- |
| Avg Intent Accuracy | 100.0 | 98.5 |
| Avg Output Correctness | 100.0 | 47.75 |
| Avg Latency (ms) | 0.23 | 2055 |
| Error Handling Rate | 100.0 | 100 |
| Speed Score | 10.0 | 0 |
| Composite Score (1-10,000) | 9100 | 6850 |

Detailed case-level comparison is maintained in `benchmarks/comparison.md`.

Methodology note: custom-agent latency is measured from local benchmark execution with mocked exchange responses, while baseline latency reflects chat-driven responses under plan constraints. Treat the benchmark as a relative workflow comparison.

## 7. Design decisions

Python was selected for fast iteration, broad exchange tooling, and straightforward test/automation ergonomics. `python-binance` provides mature REST bindings and reduces integration risk versus handwritten HTTP clients. Claude is used for NLU only where deterministic regex routing is insufficient, which keeps normal execution fast while still handling ambiguous language. The modular router pattern isolates parsing, orchestration, exchange access, and prompt logic so each layer can evolve independently and be benchmarked in isolation.

## 8. Security notes

No secrets should be committed. Runtime credentials are loaded from `.env`, and `.env.example` provides the contract without exposing real values. `.gitignore` excludes `.env`, cache artifacts, and common key formats. API calls are wrapped with explicit error handling, and dry-run mode is on by default to prevent accidental live orders during development.

## 9. Cursor integration guide

This project is configured for Cursor-driven development through `.cursorrules` and a dedicated system prompt file. Open the `agent` directory in Cursor so rules are applied to code generation. Keep `.cursorrules` focused on non-negotiable engineering constraints (env-only secrets, modular boundaries, router-first command registration, short functions, type hints, robust API error handling). Keep behavior-level NLU instructions in `system_prompt.txt`, not in source code strings, so prompt updates are versioned and reviewable. After adding any command, run the evaluator and update benchmark artifacts to verify no regressions.
