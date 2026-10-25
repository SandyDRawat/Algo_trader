"""Backtest engine. Honest by construction:
- signals are read on bar close and filled at the NEXT bar's open (no look-ahead),
- indicators warm up on the full history before the test window starts,
- every fill pays slippage and real Indian charges (costs.py),
- stops/targets fill at the level, or at the open if price gapped through it; if both are hit
  inside one bar the stop wins (we can't know the order, so assume the worse case).
"""
import math

import numpy as np
import pandas as pd

from . import data
from .costs import RATES_AS_OF, charges
from .strategy import Strategy, signals, term

OVERLAYS = {"sma", "ema", "bb_upper", "bb_lower", "bb_mid", "highest", "lowest", "supertrend"}


def run(s: Strategy, df: pd.DataFrame | None = None):
    full = data.bars(s.symbol, s.timeframe) if df is None else df
    entry, exit_ = signals(full, s)
    window = (full.index >= pd.Timestamp(s.start or full.index[0])) & (full.index <= pd.Timestamp(s.end or full.index[-1]) + pd.Timedelta(days=1))
    df, entry, exit_ = full[window], entry[window].tolist(), exit_[window].tolist()
    if len(df) < 2:
        raise ValueError("Not enough bars in that date range.")
    overlays = {}  # price-scale indicators the rules use, for drawing on the chart
    for cnd in (s.entry + s.exit) if s.kind == "rules" else []:
        for side in (cnd.left, cnd.right):
            if isinstance(side, str) and side.split("(")[0].strip().lower() in OVERLAYS and side not in overlays:
                overlays[side] = curve(term(full, side)[window].dropna())

    o, h, l, c = (df[k].to_numpy().tolist() for k in ("open", "high", "low", "close"))
    t = df.index
    n, sign, slip = len(df), (1 if s.direction == "long" else -1), s.slippage_pct / 100
    intraday = (t.normalize() != t).any()
    day = t.normalize()
    last_of_day = np.r_[day[1:] != day[:-1], True] if intraday else np.zeros(n, bool)
    squareoff = pd.Timestamp(s.intraday_exit).time() if s.intraday_exit and intraday else None
    square_off_daily = intraday and (squareoff or s.segment == "equity_intraday")

    cash, qty, px, opened, cost_total = s.capital, 0, 0.0, 0, 0.0
    trades, equity, costs_cum = [], np.empty(n), np.empty(n)

    def close(i, raw, reason):
        nonlocal cash, qty, cost_total
        fill = raw * (1 - sign * slip)
        side = "sell" if sign == 1 else "buy"
        fee = charges(s.segment, side, fill, qty)
        gross = sign * qty * (fill - px)
        cash += gross - fee
        cost_total += fee + qty * abs(raw - fill)
        tr = trades[-1]
        tr.update(exit_time=t[i], exit_price=round(fill, 2), pnl=round(tr["pnl"] + gross - fee, 2),
                  charges=round(tr["charges"] + fee, 2), bars=i - opened, reason=reason)
        tr["return_pct"] = round(tr["pnl"] / (tr["entry_price"] * tr["qty"]) * 100, 2)
        qty = 0

    for i in range(n):
        if i and qty and (exit_[i - 1] or (s.max_bars and i - opened >= s.max_bars)):
            close(i, o[i], "signal" if exit_[i - 1] else "time")
        can_enter = not (squareoff and t[i].time() >= squareoff) and not last_of_day[i]
        if i and not qty and entry[i - 1] and can_enter:
            fill = o[i] * (1 + sign * slip)
            q = math.floor(cash * s.position_pct / 100 / fill)
            if q > 0:
                side = "buy" if sign == 1 else "sell"
                fee = charges(s.segment, side, fill, q)
                cash -= fee
                cost_total += fee + q * abs(fill - o[i])
                qty, px, opened = q, fill, i
                trades.append(dict(entry_time=t[i], entry_price=round(fill, 2), qty=q, side=s.direction,
                                   pnl=-round(fee, 2), charges=round(fee, 2)))
        if qty:
            stop = px * (1 - sign * s.stop_loss_pct / 100) if s.stop_loss_pct else None
            target = px * (1 + sign * s.take_profit_pct / 100) if s.take_profit_pct else None
            worst, best = (l[i], h[i]) if sign == 1 else (h[i], l[i])
            if stop is not None and sign * (worst - stop) <= 0:
                close(i, o[i] if sign * (o[i] - stop) < 0 and i > opened else stop, "stop")
            elif target is not None and sign * (best - target) >= 0:
                close(i, o[i] if sign * (o[i] - target) > 0 and i > opened else target, "target")
        if qty and square_off_daily and (last_of_day[i] or (squareoff and t[i].time() >= squareoff)):
            close(i, c[i], "square-off")
        if qty and i == n - 1:
            close(i, c[i], "end of data")
        equity[i] = cash + (sign * qty * (c[i] - px) if qty else 0)
        costs_cum[i] = cost_total

    eq = pd.Series(equity, index=t)
    return report(s, df, eq, pd.Series(equity + costs_cum, index=t), trades, cost_total) | {"overlays": overlays}


def cagr(series, years):
    return ((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1) * 100 if years > 0 and series.iloc[-1] > 0 else -100.0


def report(s, df, eq, gross, trades, cost_total):
    years = max((eq.index[-1] - eq.index[0]).days / 365.25, 1 / 365)
    start_eq = pd.concat([pd.Series([s.capital], index=[eq.index[0] - pd.Timedelta(seconds=1)]), eq])
    daily = eq.resample("1D").last().dropna()
    rets = daily.pct_change().dropna()
    dd = eq / eq.cummax() - 1
    bench = df["close"] / df["close"].iloc[0] * s.capital
    pnls = np.array([tr["pnl"] for tr in trades]) if trades else np.array([])
    wins, losses = pnls[pnls > 0], pnls[pnls <= 0]
    trough = dd.idxmin()
    peak = eq[:trough].idxmax()
    in_mkt = sum(tr["bars"] for tr in trades) / len(eq) * 100
    m = dict(
        start=str(eq.index[0].date()), end=str(eq.index[-1].date()), years=round(years, 2),
        final_equity=round(eq.iloc[-1], 2), total_return_pct=round((eq.iloc[-1] / s.capital - 1) * 100, 2),
        cagr_pct=round(cagr(start_eq, years), 2),
        cagr_before_costs_pct=round(cagr(pd.concat([start_eq.iloc[:1], gross]), years), 2),
        max_drawdown_pct=round(dd.min() * 100, 2), drawdown_from=str(peak.date()), drawdown_to=str(trough.date()),
        sharpe=round(rets.mean() / rets.std() * math.sqrt(252), 2) if len(rets) > 2 and rets.std() > 0 else 0.0,
        trades=len(trades), win_rate_pct=round(len(wins) / len(pnls) * 100, 1) if len(pnls) else 0.0,
        avg_win=round(wins.mean(), 2) if len(wins) else 0.0, avg_loss=round(losses.mean(), 2) if len(losses) else 0.0,
        profit_factor=round(wins.sum() / -losses.sum(), 2) if len(losses) and losses.sum() < 0 else None,
        costs=round(cost_total, 2), exposure_pct=round(in_mkt, 1),
        benchmark_return_pct=round((bench.iloc[-1] / s.capital - 1) * 100, 2),
        benchmark_cagr_pct=round(cagr(pd.concat([start_eq.iloc[:1], bench]), years), 2),
        rates_as_of=RATES_AS_OF,
    )
    return dict(strategy=s.model_dump(), metrics=m, insights=insights(s, m, trades),
                equity=curve(eq), benchmark=curve(bench), drawdown=curve(dd * 100),
                trades=[{**tr, "entry_time": str(tr["entry_time"]), "exit_time": str(tr.get("exit_time"))} for tr in trades])


def curve(series, max_points=4000):
    if series.empty:
        return []
    step = max(1, len(series) // max_points)  # ponytail: plain decimation, fine for a chart
    pts = series.iloc[::step]
    if pts.index[-1] != series.index[-1]:
        pts = pd.concat([pts, series.iloc[-1:]])
    return [{"time": int(ts.timestamp()), "value": round(float(v), 2)} for ts, v in pts.items()]


def insights(s, m, trades):
    """Plain-English coaching. Deterministic, so it's free and never invents numbers."""
    out = []
    if m["trades"] == 0:
        return ["No trades fired. Loosen the entry rule or widen the date range."]
    if m["trades"] < 30:
        out.append(f"Only {m['trades']} trades: too few to trust. Test a longer period before believing this.")
    gap = m["cagr_before_costs_pct"] - m["cagr_pct"]
    out.append(f"Charges and slippage cost ₹{m['costs']:,.0f}. They take CAGR from {m['cagr_before_costs_pct']}% to {m['cagr_pct']}%"
               + (" — costs are eating most of the edge." if gap > abs(m["cagr_pct"]) else "."))
    diff = m["cagr_pct"] - m["benchmark_cagr_pct"]
    out.append(f"{'Beat' if diff > 0 else 'Lagged'} simply holding {s.symbol} by {abs(diff):.1f}%/yr "
               f"({m['cagr_pct']}% vs {m['benchmark_cagr_pct']}%), while in the market {m['exposure_pct']}% of the time.")
    out.append(f"Worst drawdown {m['max_drawdown_pct']}% ({m['drawdown_from']} → {m['drawdown_to']}). Could you sit through that with real money?")
    stops = sum(tr.get("reason") == "stop" for tr in trades)
    if stops:
        out.append(f"{stops} of {m['trades']} trades ({stops / m['trades']:.0%}) ended at the stop-loss.")
    if m["win_rate_pct"] < 45 and m["avg_loss"] and m["avg_win"] > 2 * -m["avg_loss"]:
        out.append("Low win rate but big winners: a trend-following profile. Expect long losing streaks.")
    elif m["win_rate_pct"] > 60 and m["avg_loss"] and -m["avg_loss"] > 2 * m["avg_win"]:
        out.append("High win rate but losses are much bigger than wins: one bad trade can wipe out many good ones.")
    if s.symbol == "NIFTY" and s.segment in ("futures", "options"):
        out.append("Tested on NIFTY spot index prices. Real futures/options add lot sizes, basis and premium decay.")
    return out
