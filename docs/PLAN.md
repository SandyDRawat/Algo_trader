# AlgoTrader v2: plan

**Goal:** an Indian-market strategy lab people actually use for learning: describe or pick a strategy, backtest it
honestly, practise it by hand, paper-trade it. Self-hostable, plus a hosted version for everyday traders.

## What traders told us (Reddit, Oct 2026)
r/IndianStreetBets, r/IndianStockMarket, r/StockMarketIndia, r/IndiaAlgoTrading:
1. **Historical F&O data is the #1 pain**: minute-level options, option chains and historical Greeks are paid or missing.
2. **Backtests beat live results** because costs/slippage are ignored ("from 20% CAGR to loss-making"); STT rose Apr 2026.
3. **Tools are rigid**: template strategies, no custom expiry/time rules, ATM strike drift handled badly.
4. **Data cleaning eats the time**: splits, corporate actions, survivorship in index constituents.
5. **Paper trading feels fake**: unlimited fills at the day's low, a "Richie Rich wallet", no consequence for losing.
6. Demand for **plain-English strategy building** and **historical replay practice**.

## Decisions
- One codebase: self-host (free) and a hosted site. No broker needed for backtesting/replay; brokers are only for
  importing your portfolio (later: execution).
- Free data first: bundled NIFTY 1-min (2015–2024), CSV upload, Yahoo daily (self-host only). Intraday for the hosted
  site later via a licensed vendor (TrueData / Global Datafeeds, quote-only pricing + NSE per-user fee).
- Own small engine instead of backtesting.py (AGPL) or vectorbt (Commons Clause): both conflict with our licence.
- One strategy shape (JSON rules) shared by the form, the chat bot and the MCP server.
- OpenAlgo (AGPL) for broker connectivity and live paper trading, run as a separate service over its API; never
  copied into this codebase, so our licence stays ours.
- Licence: source-available. Free for personal use; derivative work must be published; commercial use or use with
  other people's money needs a paid licence (draft in LICENSE, pending legal review).

## Phases
### Phase 1: this PR ✅
- Engine: next-bar fills, warm-up before window, stops/targets with gap handling, shorts, square-off, real charges.
- 14 indicators, rule parser (whitelist only, no code execution), 8 presets, optional local Python strategies.
- Metrics + benchmark + "before costs" CAGR + plain-English coaching notes.
- Web app: Strategy Lab (presets, rule builder, chat, charts with trade markers and indicator overlays, trade CSV),
  Replay & Paper (bar-by-bar, server-priced fills, accounts that blow up at a loss limit, trade journal note),
  Portfolio (paper accounts, broker stubs), Data (datasets, CSV upload, Yahoo fetch), Connect-an-AI page.
- MCP server (stdio + streamable HTTP): list_datasets, list_presets, strategy_schema, run_backtest.

### Phase 2: data + F&O (next)
- NSE bhavcopy ingester: equity + F&O end-of-day since 2016, index constituents, corporate actions (adjusted prices).
- Options: contract selection by expiry (weekly/monthly) and strike (ATM±n) fixed at entry; Black-Scholes IV/Greeks
  computed from bhavcopy prices (fixes the "no historical Greeks" gap); lot sizes; multi-leg (straddle, iron condor).
- Futures: continuous series with roll dates, lot sizes, margin.
- Parquet/DuckDB store; data-quality report per dataset.
- ✅ before launch: confirm NSE terms for displaying EOD data on the hosted site.

### Phase 3: research quality
- Walk-forward / out-of-sample split, parameter sweeps with an overfitting warning, Monte Carlo of trade order.
- Multi-symbol portfolios (e.g. Nifty 50 universe with point-in-time constituents), position sizing by ATR/risk %.
- Time-of-day / weekday / expiry-day rule terms; strategy comparison view; share a strategy by link.

### Phase 4: live paper + brokers
- OpenAlgo sidecar: live quotes + sandbox paper trading of a saved strategy (forward test), alerts.
- Read-only broker portfolio import (holdings, P&L) via OpenAlgo connectors, Tickertape-style connect.
- Later: live execution with risk limits (max loss/day, kill switch), within SEBI retail-algo rules (static IP,
  10 orders/sec, daily logout; vendor registration if we host execution).

### Phase 5: hosted
- Accounts/auth, per-user data isolation, rate limits on backtests and chat, usage-based chat cost caps.
- Licensed intraday data tier.

## Risks
- Data licensing for the hosted site (EOD display, vendor redistribution).
- Chat cost on the hosted site: needs per-user caps.
- Regulatory: no advice, no return promises; execution features must follow SEBI retail-algo framework.

## Strategy library findings (Oct 2026)
36 built-in strategies: 8 classics, 19 from published research, 9 AI-discovered (tuned 2015–20, kept only if positive
after costs on 2021–24 too). On NIFTY spot after Indian costs:
- Trend/momentum works (EMA 20/50, Turtle, 200-day filter, CCI/Keltner/stochastic strength), mostly by cutting drawdown;
  few beat buy-and-hold outright in a bull market.
- Turn-of-the-month is the strongest calendar effect (positive in both periods).
- Short-term mean reversion from US research (Connors RSI(2), IBS, Double 7) fails on 2015–20 NIFTY, even gross.
- Simple intraday ideas (ORB, previous-day-high breakout, gap fade/fill) lose heavily: the gross edge is smaller than costs.
- Overnight drift is real (+0.1%/day gross) but round-trip costs erase it.
Wanted next (from the discovery run): arithmetic between terms, daily indicators on intraday bars, bars-since-entry,
once-per-day entry, expiry-day term, set membership (month in 2,3).
