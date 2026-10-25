"""Market data: bundled NIFTY 1-minute history, user CSV uploads, and (optional) Yahoo daily data.

ponytail: CSV + in-memory cache. Move to Parquet/DuckDB when datasets outgrow RAM.
"""
import os
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA = Path(os.environ.get("ALGO_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
BUILTIN = {"NIFTY": DATA / "NIFTY50-Minute_data.csv"}
USER = DATA / "user"
CACHE = DATA / "cache"
TIMEFRAMES = {"1min": "1min", "5min": "5min", "15min": "15min", "1h": "60min", "1D": "1D", "1W": "W-FRI"}
SYMBOL = re.compile(r"^[A-Z0-9&_.\-^]{1,30}$")


def read_csv(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"datetime": "date", "time": "date", "timestamp": "date"})
    missing = {"date", "open", "high", "low", "close"} - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"])
    if "volume" not in df:
        df["volume"] = 0
    df = df.set_index("date").sort_index()[["open", "high", "low", "close", "volume"]].astype(float)
    df = df[~df.index.duplicated()].dropna()
    if (df.index.normalize() != df.index).any():
        df = df.between_time("09:15", "15:29")  # intraday: keep NSE session only
    return df


def path_for(symbol):
    if symbol in BUILTIN:
        return BUILTIN[symbol]
    if not SYMBOL.match(symbol):
        raise ValueError(f"Bad symbol {symbol!r}")
    for p in (USER / f"{symbol}.csv", CACHE / f"{symbol}.csv"):
        if p.exists():
            return p
    if symbol.endswith((".NS", ".BO")) or symbol.startswith("^"):
        return fetch_yahoo(symbol)
    raise ValueError(f"No data for {symbol}. Upload a CSV, or use a Yahoo symbol like RELIANCE.NS.")


def fetch_yahoo(symbol):
    # Yahoo's terms allow personal/research use only; fine for self-hosting, not for the hosted site.
    try:
        import yfinance as yf
    except ImportError:
        raise ValueError("Install the 'yahoo' extra (uv sync --extra yahoo) to fetch NSE stocks.")
    df = yf.download(symbol, period="max", interval="1d", auto_adjust=True, progress=False, multi_level_index=False)
    if df.empty:
        raise ValueError(f"Yahoo has no data for {symbol}")
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{symbol}.csv"
    df.rename_axis("date").to_csv(out)
    return out


@lru_cache(maxsize=16)
def load(symbol):
    return read_csv(path_for(symbol))


@lru_cache(maxsize=32)
def bars(symbol, timeframe="1D"):
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"Timeframe must be one of {', '.join(TIMEFRAMES)}")
    df = load(symbol)
    rule = TIMEFRAMES[timeframe]
    intraday_src = (df.index.normalize() != df.index).any()
    if timeframe in ("1D", "1W") or not intraday_src:
        if not intraday_src and timeframe not in ("1D", "1W"):
            raise ValueError(f"{symbol} only has daily data; pick 1D or 1W.")
        out = df.resample(rule).agg(AGG)
    else:
        # Clock-aligned bins; the 15-min offset makes hourly bars start at 09:15. Overnight bins are empty and dropped.
        out = df.resample(rule, offset="15min" if rule == "60min" else None).agg(AGG)
    return out.dropna(subset=["open"])


AGG = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}


def datasets():
    names = list(BUILTIN) + sorted({p.stem for d in (USER, CACHE) if d.exists() for p in d.glob("*.csv")})
    out = []
    for s in names:
        try:
            df = load(s)
        except (ValueError, OSError):
            continue
        intraday = bool((df.index.normalize() != df.index).any())
        out.append({"symbol": s, "start": str(df.index[0].date()), "end": str(df.index[-1].date()),
                    "timeframes": list(TIMEFRAMES) if intraday else ["1D", "1W"],
                    "source": "bundled" if s in BUILTIN else "yahoo" if (CACHE / f"{s}.csv").exists() else "upload"})
    return out


def save_upload(symbol, raw: bytes):
    symbol = symbol.upper()
    if not SYMBOL.match(symbol) or symbol in BUILTIN:
        raise ValueError("Pick a different symbol name (letters, digits, . - _ only).")
    USER.mkdir(parents=True, exist_ok=True)
    tmp = USER / f".{symbol}.tmp"
    tmp.write_bytes(raw)
    try:
        read_csv(tmp)  # validate before it becomes visible
    except Exception:
        tmp.unlink()
        raise
    tmp.replace(USER / f"{symbol}.csv")
    load.cache_clear()
    bars.cache_clear()
    return symbol
