"""Strategy = a JSON rule spec. The form builder, the chat bot and MCP clients all produce this
one shape, so the engine only ever sees one thing.

Rule terms: a number, a price column (open/high/low/close/volume) or an indicator call such as
`sma(50)` / `bb_lower(20, 2)`. Terms are parsed against a whitelist, never executed as code.
Self-hosters can also drop a Python file into ./strategies (see README) for anything rules can't say.
"""
import importlib.util
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from . import indicators as ind

Op = Literal["<", ">", "<=", ">=", "crosses_above", "crosses_below"]
TERM = re.compile(r"^\s*([a-z_]+)\s*(?:\(([^)]*)\))?\s*$")
CODE_DIR = Path(os.environ.get("ALGO_STRATEGY_DIR", "strategies"))


class Condition(BaseModel):
    left: str = Field(description="Term, e.g. 'close', 'rsi(14)', 'sma(50)'")
    op: Op
    right: str | float = Field(description="Number or term, e.g. 30 or 'sma(200)'")


class Strategy(BaseModel):
    name: str = "My strategy"
    description: str = ""
    kind: Literal["rules", "code"] = "rules"
    code_file: str | None = Field(None, description="Only for kind='code': file name in ./strategies")
    symbol: str = "NIFTY"
    timeframe: str = Field("1D", description="1min, 5min, 15min, 1h, 1D or 1W")
    start: str | None = Field(None, description="YYYY-MM-DD")
    end: str | None = None
    direction: Literal["long", "short"] = "long"
    entry: list[Condition] = []
    entry_logic: Literal["all", "any"] = "all"
    exit: list[Condition] = []
    exit_logic: Literal["all", "any"] = "any"
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None
    max_bars: int | None = Field(None, description="Exit after this many bars in a trade")
    intraday_exit: str | None = Field(None, description="HH:MM square-off time for intraday timeframes")
    capital: float = 100_000
    position_pct: float = Field(100, description="% of current equity per trade")
    segment: Literal["equity_delivery", "equity_intraday", "futures", "options"] = "equity_delivery"
    slippage_pct: float = Field(0.05, description="Adverse slippage per fill, in %")


def term(df, t):
    if isinstance(t, (int, float)):
        return float(t)
    try:
        return float(t)
    except ValueError:
        pass
    m = TERM.match(t.lower())
    if not m:
        raise ValueError(f"Can't read term {t!r}. Use a number, a price like 'close', or e.g. 'sma(50)'.")
    name, args = m.group(1), [float(a) for a in (m.group(2) or "").split(",") if a.strip()]
    if name in ind.PRICE and not args:
        return df[name]
    if name not in ind.INDICATORS:
        raise ValueError(f"Unknown indicator {name!r}. Available: {', '.join(sorted(ind.INDICATORS))}")
    return ind.INDICATORS[name](df, *args)


def condition(df, c):
    a, b, op = term(df, c.left), term(df, c.right), c.op
    if isinstance(a, float):  # keep the series on the left so shift() works
        a, b, op = b, a, FLIP[op]
    if isinstance(a, float):
        raise ValueError("A condition needs at least one price or indicator term.")
    if op in ("crosses_above", "crosses_below"):
        b_prev = b.shift() if isinstance(b, pd.Series) else b
        if op == "crosses_above":
            return (a > b) & (a.shift() <= b_prev)
        return (a < b) & (a.shift() >= b_prev)
    return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]


FLIP = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "crosses_above": "crosses_below", "crosses_below": "crosses_above"}


def combine(df, conds, logic):
    if not conds:
        return pd.Series(False, index=df.index)
    s = [condition(df, c).fillna(False).astype(bool) for c in conds]
    out = s[0]
    for x in s[1:]:
        out = out & x if logic == "all" else out | x
    return out


def signals(df, s: Strategy):
    """Return (entry, exit) boolean Series. Signals are on bar close; the engine fills next bar."""
    if s.kind == "code":
        return load_code(s.code_file).signals(df)
    return combine(df, s.entry, s.entry_logic), combine(df, s.exit, s.exit_logic)


@lru_cache
def load_code(name):
    # Security boundary: only local files a self-hoster put in ./strategies, never uploaded code.
    if os.environ.get("ALGO_ALLOW_CODE") != "1":
        raise ValueError("Code strategies are disabled. Set ALGO_ALLOW_CODE=1 (self-hosted only).")
    path = (CODE_DIR / Path(name or "").name).resolve()
    if path.suffix != ".py" or not path.is_file():
        raise ValueError(f"No strategy file {path.name} in {CODE_DIR}/")
    spec = importlib.util.spec_from_file_location(f"user_strategy_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def C(left, op, right):
    return Condition(left=left, op=op, right=right)


PRESETS = {p.name: p for p in [
    Strategy(name="Golden cross 50/200", description="Classic trend filter: buy when the 50-day average crosses above the 200-day, sell on the reverse cross.",
             entry=[C("sma(50)", "crosses_above", "sma(200)")], exit=[C("sma(50)", "crosses_below", "sma(200)")], start="2016-01-01"),
    Strategy(name="RSI dip buy", description="Buy oversold dips (RSI below 30), sell when RSI recovers above 55. Stop 3%.",
             entry=[C("rsi(14)", "<", 30)], exit=[C("rsi(14)", ">", 55)], stop_loss_pct=3, start="2016-01-01"),
    Strategy(name="Bollinger band bounce", description="Mean reversion: buy a close below the lower band, exit at the middle band.",
             entry=[C("close", "<", "bb_lower(20,2)")], exit=[C("close", ">", "bb_mid(20,2)")], stop_loss_pct=4, start="2016-01-01"),
    Strategy(name="MACD crossover", description="Momentum: buy when MACD crosses above its signal line, exit on the cross back.",
             entry=[C("macd(12,26,9)", "crosses_above", "macd_signal(12,26,9)")], exit=[C("macd(12,26,9)", "crosses_below", "macd_signal(12,26,9)")], start="2016-01-01"),
    Strategy(name="20-day breakout", description="Trend following: buy a close above the prior 20-day high, exit below the prior 10-day low.",
             entry=[C("close", ">", "highest(20)")], exit=[C("close", "<", "lowest(10)")], start="2016-01-01"),
    Strategy(name="Supertrend swing", description="Ride the trend while price stays above Supertrend(10,3).",
             entry=[C("close", "crosses_above", "supertrend(10,3)")], exit=[C("close", "crosses_below", "supertrend(10,3)")], start="2016-01-01"),
    Strategy(name="Trend + RSI pullback", description="Only buy dips inside an uptrend: price above the 200-day average and RSI under 40.",
             entry=[C("close", ">", "sma(200)"), C("rsi(14)", "<", 40)], exit=[C("rsi(14)", ">", 65)], stop_loss_pct=5, start="2016-01-01"),
    Strategy(name="Opening gap fade (intraday)", description="5-min NIFTY: short a gap-up above 0.7% at the open, target 0.5%, stop 0.5%, square off 15:15.",
             timeframe="5min", direction="short", segment="futures", entry=[C("gap_pct", ">", 0.7)], take_profit_pct=0.5,
             stop_loss_pct=0.5, intraday_exit="15:15", start="2023-01-01", end="2023-12-31"),
]}
