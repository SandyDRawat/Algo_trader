"""Built-in strategies: classics, published research, and AI-discovered from the bundled data.

Published rules are reproduced as faithfully as the rule language allows; where we had to approximate, the
description says so. None of these are recommendations; they're starting points to test and learn from.
"""
import json
from pathlib import Path

from .strategy import Condition, Strategy


def C(left, op, right):
    return Condition(left=left, op=op, right=right)


def S(**kw):
    kw.setdefault("start", "2016-01-01")
    return Strategy(**kw)


INTRADAY = dict(timeframe="5min", segment="futures", intraday_exit="15:15", start="2021-01-01")

CLASSICS = [
    S(name="Golden cross 50/200", category="trend", source="Classic",
      description="Buy when the 50-day average crosses above the 200-day, sell on the reverse cross.",
      entry=[C("sma(50)", "crosses_above", "sma(200)")], exit=[C("sma(50)", "crosses_below", "sma(200)")]),
    S(name="RSI dip buy", category="mean-reversion", source="Classic",
      description="Buy oversold dips (RSI below 30), sell when RSI recovers above 55. Stop 3%.",
      entry=[C("rsi(14)", "<", 30)], exit=[C("rsi(14)", ">", 55)], stop_loss_pct=3),
    S(name="Bollinger band bounce", category="mean-reversion", source="John Bollinger",
      description="Buy a close below the lower band, exit at the middle band. Stop 4%.",
      entry=[C("close", "<", "bb_lower(20,2)")], exit=[C("close", ">", "bb_mid(20,2)")], stop_loss_pct=4),
    S(name="MACD crossover", category="momentum", source="Gerald Appel",
      description="Buy when MACD crosses above its signal line, exit on the cross back.",
      entry=[C("macd(12,26,9)", "crosses_above", "macd_signal(12,26,9)")], exit=[C("macd(12,26,9)", "crosses_below", "macd_signal(12,26,9)")]),
    S(name="20-day breakout", category="breakout", source="Classic",
      description="Buy a close above the prior 20-day high, exit below the prior 10-day low.",
      entry=[C("close", ">", "highest(20)")], exit=[C("close", "<", "lowest(10)")]),
    S(name="Supertrend swing", category="trend", source="Olivier Seban",
      description="Ride the trend while price stays above Supertrend(10,3).",
      entry=[C("close", "crosses_above", "supertrend(10,3)")], exit=[C("close", "crosses_below", "supertrend(10,3)")]),
    S(name="Trend + RSI pullback", category="mean-reversion", source="Classic",
      description="Only buy dips inside an uptrend: price above the 200-day average and RSI under 40.",
      entry=[C("close", ">", "sma(200)"), C("rsi(14)", "<", 40)], exit=[C("rsi(14)", ">", 65)], stop_loss_pct=5),
    S(name="Opening gap fade (intraday)", category="intraday", source="Classic", **{**INTRADAY, "start": "2023-01-01", "end": "2023-12-31"},
      description="Short a gap-up above 0.7% at the open, target 0.5%, stop 0.5%, square off 15:15.",
      direction="short", entry=[C("gap_pct", ">", 0.7)], take_profit_pct=0.5, stop_loss_pct=0.5),
]

RESEARCH = [
    # --- Larry Connors & short-term mean reversion -------------------------------------------
    S(name="Connors RSI(2)", segment="futures", category="mean-reversion", source="Larry Connors, Short Term Trading Strategies That Work (2008)",
      description="In an uptrend (close above 200-day SMA) buy when 2-day RSI drops below 10; sell when close rises above the 5-day SMA.",
      entry=[C("close", ">", "sma(200)"), C("rsi(2)", "<", 10)], exit=[C("close", ">", "sma(5)")]),
    S(name="Connors Double 7", segment="futures", category="mean-reversion", source="Larry Connors & Cesar Alvarez",
      description="Above the 200-day SMA, buy a close at a new 7-day closing low; sell at a new 7-day closing high.",
      entry=[C("close", ">", "sma(200)"), C("close", "<", "lowest_close(7)")], exit=[C("close", ">", "highest_close(7)")]),
    S(name="Three down days", segment="futures", category="mean-reversion", source="Larry Connors (3-day pullback)",
      description="Above the 200-day SMA, buy after three lower closes in a row; sell when close is back above the 5-day SMA.",
      entry=[C("close", ">", "sma(200)"), C("down_streak", ">=", 3)], exit=[C("close", ">", "sma(5)")]),
    S(name="Internal bar strength", segment="futures", category="mean-reversion", source="Academic: Pagonidis (2013), IBS effect",
      description="Buy when the day closes in the bottom 20% of its range; sell when a day closes in the top 20%.",
      entry=[C("ibs", "<", 0.2)], exit=[C("ibs", ">", 0.8)], stop_loss_pct=4),
    S(name="Williams %R(2) washout", segment="futures", category="mean-reversion", source="Larry Williams",
      description="Above the 200-day SMA, buy when 2-day %R falls under -90; sell when it rises above -20.",
      entry=[C("close", ">", "sma(200)"), C("williams_r(2)", "<", -90)], exit=[C("williams_r(2)", ">", -20)]),
    S(name="Stochastic oversold in uptrend", segment="futures", category="mean-reversion", source="George Lane (stochastics)",
      description="Above the 200-day SMA, buy when %K(14) is under 20; sell when it climbs above 80.",
      entry=[C("close", ">", "sma(200)"), C("stoch_k(14)", "<", 20)], exit=[C("stoch_k(14)", ">", 80)]),
    S(name="CCI comeback", segment="futures", category="mean-reversion", source="Donald Lambert (CCI)",
      description="Buy when CCI(20) climbs back above -100 from oversold; sell when it reaches +100. Stop 4%.",
      entry=[C("cci(20)", "crosses_above", -100)], exit=[C("cci(20)", ">", 100)], stop_loss_pct=4),
    # --- Trend following ------------------------------------------------------------------------
    S(name="Turtle 55/20 breakout", category="trend", source="Richard Dennis' Turtles (System 2)",
      description="Buy a close above the prior 55-day high; exit on a close below the prior 20-day low.",
      entry=[C("close", ">", "highest(55)")], exit=[C("close", "<", "lowest(20)")]),
    S(name="200-day trend filter", category="trend", source="Meb Faber, A Quantitative Approach to TAA (2007)",
      description="Hold NIFTY only while it closes above its 200-day average (Faber's 10-month rule, daily version).",
      entry=[C("close", "crosses_above", "sma(200)")], exit=[C("close", "crosses_below", "sma(200)")]),
    S(name="Time-series momentum (6M)", category="momentum", source="Moskowitz, Ooi & Pedersen (2012)",
      description="Hold while the 6-month (126-day) return is positive; step aside when it turns negative.",
      entry=[C("pct_change(126)", ">", 0)], exit=[C("pct_change(126)", "<", 0)]),
    S(name="ADX trend rider", category="trend", source="J. Welles Wilder (ADX)",
      description="Buy when the trend is strong (ADX(14) above 25) and price is above the 50-day EMA; exit below the EMA.",
      entry=[C("adx(14)", ">", 25), C("close", ">", "ema(50)")], exit=[C("close", "<", "ema(50)")]),
    S(name="Keltner channel breakout", category="breakout", source="Chester Keltner / Linda Raschke",
      description="Buy a close above the upper Keltner channel (EMA20 + 2×ATR); exit when price closes back below the EMA20.",
      entry=[C("close", ">", "keltner_upper(20,2)")], exit=[C("close", "<", "ema(20)")]),
    S(name="EMA 20/50 crossover", category="trend", source="Classic",
      description="Faster cousin of the golden cross: buy when EMA20 crosses above EMA50, exit on the cross down.",
      entry=[C("ema(20)", "crosses_above", "ema(50)")], exit=[C("ema(20)", "crosses_below", "ema(50)")]),
    S(name="NR7 squeeze", segment="futures", category="volatility", source="Toby Crabel, Day Trading with Short Term Price Patterns (1990)",
      description="After the narrowest range of 7 days in an uptrend, buy and hold 5 days (stop 2%). Approximation of Crabel's NR7 breakout.",
      entry=[C("nr(7)", ">=", 1), C("close", ">", "sma(50)")], max_bars=5, stop_loss_pct=2),
    # --- Calendar -------------------------------------------------------------------------------
    S(name="Turn of the month", segment="futures", category="calendar", source="Ariel (1987); Lakonishok & Smidt (1988)",
      description="Buy 4 sessions before month-end, sell after the 3rd session of the new month. Out of the market otherwise.",
      entry=[C("tdleft", "==", 4)], exit=[C("tdom", "==", 3)]),
    # --- Intraday (NIFTY 5-min, futures costs) ---------------------------------------------------
    S(name="Opening range breakout (15m)", category="intraday", source="Toby Crabel / classic ORB", **INTRADAY,
      description="Buy when price breaks above the first 15 minutes' high before 11:00. Stop 0.4%, target 0.8%, out by 15:15.",
      entry=[C("close", "crosses_above", "or_high(3)"), C("hhmm", "<", 1100)], stop_loss_pct=0.4, take_profit_pct=0.8),
    S(name="Opening range breakdown (15m)", category="intraday", source="Toby Crabel / classic ORB", **INTRADAY,
      description="Short when price breaks below the first 15 minutes' low before 11:00. Stop 0.4%, target 0.8%, out by 15:15.",
      direction="short", entry=[C("close", "crosses_below", "or_low(3)"), C("hhmm", "<", 1100)], stop_loss_pct=0.4, take_profit_pct=0.8),
    S(name="Previous-day high breakout", category="intraday", source="Classic PDH/PDL trading", **INTRADAY,
      description="Buy when NIFTY breaks above yesterday's high before 13:00. Stop 0.4%, target 0.8%, out by 15:15.",
      entry=[C("close", "crosses_above", "prev_high"), C("hhmm", "<", 1300)], stop_loss_pct=0.4, take_profit_pct=0.8),
    S(name="Gap-down fill", category="intraday", source="Classic gap trading", **INTRADAY,
      description="After a gap down of 0.5%+, buy at 9:20 aiming for the gap to fill toward yesterday's close. Stop 0.6%.",
      entry=[C("gap_pct", "<", -0.5)], exit=[C("close", ">=", "prev_close")], stop_loss_pct=0.6),
]

# Strategies an AI agent found by mining the bundled NIFTY data (tuned on 2015–2020, checked on 2021–2024).
AI_FILE = Path(__file__).with_name("presets_ai.json")
AI_DISCOVERED = [Strategy.model_validate(s) for s in json.loads(AI_FILE.read_text())] if AI_FILE.exists() else []

PRESETS = {p.name: p for p in CLASSICS + RESEARCH + AI_DISCOVERED}
