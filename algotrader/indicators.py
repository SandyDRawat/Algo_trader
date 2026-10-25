"""Indicators as plain pandas functions: (df, *params) -> Series.

Every function here is callable from a strategy rule as `name(args)`,
e.g. `sma(50)`, `bb_upper(20, 2)`, `rsi(14)`.
"""
import numpy as np
import pandas as pd


def sma(df, n=20):
    return df["close"].rolling(int(n)).mean()


def ema(df, n=20):
    return df["close"].ewm(span=int(n), adjust=False).mean()


def rsi(df, n=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + gain / loss.replace(0, np.nan))


def bb_mid(df, n=20, k=2):
    return sma(df, n)


def bb_upper(df, n=20, k=2):
    return sma(df, n) + k * df["close"].rolling(int(n)).std()


def bb_lower(df, n=20, k=2):
    return sma(df, n) - k * df["close"].rolling(int(n)).std()


def macd(df, fast=12, slow=26, signal=9):
    return ema(df, fast) - ema(df, slow)


def macd_signal(df, fast=12, slow=26, signal=9):
    return macd(df, fast, slow).ewm(span=int(signal), adjust=False).mean()


def atr(df, n=14):
    prev = df["close"].shift()
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def highest(df, n=20):
    """Highest high of the previous n bars (excludes the current bar, so breakouts are tradeable)."""
    return df["high"].rolling(int(n)).max().shift()


def lowest(df, n=20):
    return df["low"].rolling(int(n)).min().shift()


def highest_close(df, n=7):
    """Highest close of the previous n bars."""
    return df["close"].rolling(int(n)).max().shift()


def lowest_close(df, n=7):
    return df["close"].rolling(int(n)).min().shift()


def pct_change(df, n=1):
    return df["close"].pct_change(int(n)) * 100


def gap_pct(df):
    """Day's opening gap vs the previous day's close, in %. Only set on the first bar of each day."""
    day = df.index.normalize()
    first = np.r_[True, day[1:] != day[:-1]]
    return ((df["open"] / df["close"].shift() - 1) * 100).where(first, 0.0)


def supertrend(df, n=10, k=3):
    """Supertrend line; price above it = uptrend."""
    a, hl2 = atr(df, n), (df["high"] + df["low"]) / 2
    up, dn = (hl2 - k * a).to_numpy(copy=True), (hl2 + k * a).to_numpy(copy=True)
    close = df["close"].to_numpy()
    line, trend = np.full(len(df), np.nan), 1
    for i in range(1, len(df)):
        if np.isnan(a.iat[i]):
            continue
        if close[i - 1] > up[i - 1] and not np.isnan(up[i - 1]):
            up[i] = max(up[i], up[i - 1])
        if close[i - 1] < dn[i - 1] and not np.isnan(dn[i - 1]):
            dn[i] = min(dn[i], dn[i - 1])
        trend = 1 if close[i] > dn[i - 1] else -1 if close[i] < up[i - 1] else trend
        line[i] = up[i] if trend == 1 else dn[i]
    return pd.Series(line, index=df.index)


def adx(df, n=14):
    """Trend strength 0-100 (Wilder). Above ~25 = trending."""
    up, dn = df["high"].diff(), -df["low"].diff()
    plus = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    minus = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    a = atr(df, n)
    pdi = 100 * plus.ewm(alpha=1 / n, adjust=False).mean() / a
    mdi = 100 * minus.ewm(alpha=1 / n, adjust=False).mean() / a
    return (100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)).ewm(alpha=1 / n, adjust=False).mean()


def stoch_k(df, n=14):
    lo, hi = df["low"].rolling(int(n)).min(), df["high"].rolling(int(n)).max()
    return 100 * (df["close"] - lo) / (hi - lo).replace(0, np.nan)


def williams_r(df, n=14):
    return stoch_k(df, n) - 100


def cci(df, n=20):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mad = tp.rolling(int(n)).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    return (tp - tp.rolling(int(n)).mean()) / (0.015 * mad)


def ibs(df):
    """Internal bar strength: where the close sits in the bar's range, 0 (low) to 1 (high)."""
    return (df["close"] - df["low"]) / (df["high"] - df["low"]).replace(0, np.nan)


def keltner_upper(df, n=20, k=2):
    return ema(df, n) + k * atr(df, n)


def keltner_lower(df, n=20, k=2):
    return ema(df, n) - k * atr(df, n)


def down_streak(df):
    """How many closes in a row were lower than the one before."""
    d = df["close"] < df["close"].shift()
    return d.groupby((~d).cumsum()).cumsum().astype(float)


def up_streak(df):
    u = df["close"] > df["close"].shift()
    return u.groupby((~u).cumsum()).cumsum().astype(float)


def nr(df, n=7):
    """1 when this bar's range is the narrowest of the last n bars (NR7 when n=7)."""
    rng = df["high"] - df["low"]
    return (rng <= rng.rolling(int(n)).min()).astype(float)


# --- calendar & session terms -------------------------------------------------
def dow(df):
    """Day of week: 0=Mon … 4=Fri."""
    return pd.Series(df.index.dayofweek, index=df.index, dtype=float)


def month(df):
    return pd.Series(df.index.month, index=df.index, dtype=float)


def hhmm(df):
    """Bar time as a number, e.g. 915 or 1430 (intraday only)."""
    return pd.Series(df.index.hour * 100 + df.index.minute, index=df.index, dtype=float)


def _days(df):
    day = df.index.normalize()
    daily = df.groupby(day).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
    return day, daily


def _per_day(df, daily_series):
    day, _ = _days(df)
    return pd.Series(daily_series.reindex(day).to_numpy(), index=df.index)


def prev_close(df):
    _, d = _days(df)
    return _per_day(df, d["close"].shift())


def prev_high(df):
    _, d = _days(df)
    return _per_day(df, d["high"].shift())


def prev_low(df):
    _, d = _days(df)
    return _per_day(df, d["low"].shift())


def day_open(df):
    _, d = _days(df)
    return _per_day(df, d["open"])


def tdom(df):
    """Trading day of the month: 1 = first session of the month."""
    _, d = _days(df)
    return _per_day(df, d.groupby(d.index.to_period("M")).cumcount().astype(float) + 1)


def tdleft(df):
    """Trading sessions left in the month after this one: 0 = last session."""
    _, d = _days(df)
    g = d.groupby(d.index.to_period("M"))
    return _per_day(df, (g["close"].transform("size") - g.cumcount() - 1).astype(float))


def _opening_range(df, n, col, how):
    day = df.index.normalize()
    k = df.groupby(day).cumcount()
    rng = df[col].where(k < n).groupby(day).transform(how)
    return rng.where(k >= n)  # only known once the first n bars are done


def or_high(df, n=3):
    """High of the day's first n bars (e.g. 3 × 5-min = 15-min opening range). Intraday only."""
    return _opening_range(df, int(n), "high", "max")


def or_low(df, n=3):
    return _opening_range(df, int(n), "low", "min")


PRICE = {"open", "high", "low", "close", "volume"}
INDICATORS = {f.__name__: f for f in [
    sma, ema, rsi, bb_mid, bb_upper, bb_lower, macd, macd_signal, atr, highest, lowest, highest_close, lowest_close,
    pct_change, gap_pct,
    supertrend, adx, stoch_k, williams_r, cci, ibs, keltner_upper, keltner_lower, down_streak, up_streak, nr,
    dow, month, hhmm, prev_close, prev_high, prev_low, day_open, tdom, tdleft, or_high, or_low]}
