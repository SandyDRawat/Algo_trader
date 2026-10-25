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


PRICE = {"open", "high", "low", "close", "volume"}
INDICATORS = {f.__name__: f for f in [sma, ema, rsi, bb_mid, bb_upper, bb_lower, macd, macd_signal, atr,
                                      highest, lowest, pct_change, gap_pct, supertrend]}
