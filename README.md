# AlgoTrader v2

Test trading ideas on Indian market data before you risk a rupee, then practise them by hand.

- **Strategy Lab**: pick one of 8 classic strategies, build rules in a form, or describe an idea in plain English.
  Backtests fill on the next bar's open and pay real Indian charges (STT, exchange, SEBI, stamp duty, GST) plus
  slippage, and a coach explains what the result means. Charts show trades and indicators.
- **Replay & Paper**: replay a real past NIFTY session candle by candle and trade it with a paper account that has
  a loss limit. Fills are priced on the server, and every trade is journalled.
- **MCP server**: any AI agent (Claude, Cursor, your own bot) can list data and run backtests.
- **Your data**: bundled NIFTY 1-minute data (2015–2024), CSV upload, or Yahoo daily data for NSE stocks (self-hosted).

For learning only. Past results are not a promise, and this is not investment advice.

## Run it

```bash
uv sync --all-extras
uv run uvicorn algotrader.api:app --port 8000      # open http://localhost:8000
uv run pytest                                      # engine tests
```

Chat needs `ANTHROPIC_API_KEY` in the server's environment (model: `ALGO_CHAT_MODEL`, default `claude-opus-5-5`).
Everything else works without it.

### Connect an AI (MCP)

```bash
claude mcp add algotrader -- uv --directory "$PWD" run python -m algotrader.mcp_server
uv run python -m algotrader.mcp_server --http       # streamable HTTP on :8001/mcp
```

### Strategy rules

A strategy is JSON: `entry` / `exit` conditions like `{"left": "rsi(14)", "op": "<", "right": 30}` plus stop-loss,
target, max bars, square-off time, capital, sizing, segment and slippage. The terms are:
- numbers
- `open high low close volume`
- `sma(n) ema(n) rsi(n) bb_upper(n,k) bb_lower(n,k) bb_mid(n,k) macd(f,s,sig) macd_signal(f,s,sig) atr(n)`
- `highest(n) lowest(n) pct_change(n) gap_pct supertrend(n,k)`

The operators are `< > <= >= crosses_above crosses_below`.

Self-hosters can write anything in Python. Put a file in `./strategies/` with
`def signals(df) -> (entry: pd.Series[bool], exit: pd.Series[bool])`, set `ALGO_ALLOW_CODE=1`, then post a strategy
with `"kind": "code", "code_file": "my_idea.py"`. This is disabled by default, and it is never for the hosted site.

### Config

| Env var | Default | |
|---|---|---|
| `ALGO_DATA_DIR` | `./data` | datasets, uploads, Yahoo cache |
| `ALGO_DB` | `data/paper.db` | paper accounts |
| `ALGO_CHAT_MODEL` | `claude-opus-5-5` | chat model |
| `ALGO_ALLOW_CODE` | off | enable `./strategies/*.py` |

Charges live in `algotrader/costs.py` (rates as of Oct 2026). Check them against your broker's contract note.

## Layout

```
algotrader/
  engine.py      backtest loop, metrics, coaching notes
  strategy.py    rule spec, term parser, presets
  indicators.py  indicator functions
  costs.py       Indian charges table
  data.py        loading, resampling, uploads, Yahoo
  paper.py       paper accounts (SQLite)
  chat.py        plain English → strategy (Claude)
  mcp_server.py  MCP tools
  api.py         FastAPI + static web app
  web/           index.html, app.js, style.css (no build step)
docs/PLAN.md     roadmap, findings, decisions
```

## Licence

Source-available. It is free for personal use, and derivative work must be published. Commercial use, or use with
other people's money, needs a paid licence. See [LICENSE](LICENSE) (draft).
