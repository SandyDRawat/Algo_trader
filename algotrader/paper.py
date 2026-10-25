"""Paper trading accounts (SQLite). Trades happen in Replay: a past session played back bar by bar.

The browser only says *which bars* you entered and exited on; prices, slippage and charges are
looked up here, so the P&L can't be fudged. An account "dies" when it loses max_loss_pct of its
starting capital, because a paper account with unlimited money teaches nothing.
"""
import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from . import data
from .costs import charges

DB = Path(os.environ.get("ALGO_DB", data.DATA / "paper.db"))
SLIPPAGE = 0.0005

SCHEMA = """
create table if not exists accounts(id integer primary key, name text not null, capital real not null,
  cash real not null, max_loss_pct real not null, status text not null default 'active',
  created text default current_timestamp);
create table if not exists trades(id integer primary key, account_id integer not null references accounts(id),
  symbol text, timeframe text, side text, qty integer, entry_time text, exit_time text,
  entry_price real, exit_price real, charges real, pnl real, note text, created text default current_timestamp);
"""


def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def create_account(name, capital, max_loss_pct=20):
    if capital <= 0 or not 0 < max_loss_pct <= 100:
        raise ValueError("Capital must be positive and max loss between 1 and 100%.")
    with closing(db()) as con, con:
        cur = con.execute("insert into accounts(name, capital, cash, max_loss_pct) values (?,?,?,?)",
                          (name.strip()[:60] or "Paper account", capital, capital, max_loss_pct))
    return account(cur.lastrowid)  # after the commit, so the new row is visible


def accounts():
    with closing(db()) as con:
        return [dict(r) for r in con.execute("select * from accounts order by id desc")]


def account(account_id):
    with closing(db()) as con:
        row = con.execute("select * from accounts where id=?", (account_id,)).fetchone()
        if not row:
            raise ValueError("No such account")
        trades = [dict(r) for r in con.execute("select * from trades where account_id=? order by id desc", (account_id,))]
    a = dict(row)
    pnls = [t["pnl"] for t in trades]
    a.update(trades=trades, realised_pnl=round(a["cash"] - a["capital"], 2),
             win_rate_pct=round(sum(p > 0 for p in pnls) / len(pnls) * 100, 1) if pnls else None,
             loss_limit=round(a["capital"] * (1 - a["max_loss_pct"] / 100), 2))
    return a


def price_at(symbol, timeframe, when):
    df = data.bars(symbol, timeframe)
    ts = pd.Timestamp(when)
    if ts not in df.index:
        raise ValueError(f"No {timeframe} bar for {symbol} at {when}")
    return float(df.at[ts, "close"])


def record_trade(account_id, symbol, timeframe, side, qty, entry_time, exit_time, segment="equity_intraday", note=""):
    a = account(account_id)
    if a["status"] != "active":
        raise ValueError("This account has hit its loss limit. Open a new one and note what went wrong.")
    if side not in ("long", "short") or qty <= 0:
        raise ValueError("side must be long/short and qty positive")
    if pd.Timestamp(exit_time) < pd.Timestamp(entry_time):
        raise ValueError("Exit must be after entry")
    sign = 1 if side == "long" else -1
    entry = price_at(symbol, timeframe, entry_time) * (1 + sign * SLIPPAGE)
    exit_ = price_at(symbol, timeframe, exit_time) * (1 - sign * SLIPPAGE)
    if entry * qty > a["cash"]:
        raise ValueError(f"Not enough capital: that needs ₹{entry * qty:,.0f}, you have ₹{a['cash']:,.0f}.")
    fee = charges(segment, "buy" if sign == 1 else "sell", entry, qty) + charges(segment, "sell" if sign == 1 else "buy", exit_, qty)
    pnl = round(sign * qty * (exit_ - entry) - fee, 2)
    cash = a["cash"] + pnl
    with closing(db()) as con, con:
        con.execute("insert into trades(account_id, symbol, timeframe, side, qty, entry_time, exit_time, entry_price,"
                    " exit_price, charges, pnl, note) values (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (account_id, symbol, timeframe, side, qty, str(entry_time), str(exit_time), round(entry, 2),
                     round(exit_, 2), round(fee, 2), pnl, note[:500]))
        con.execute("update accounts set cash=?, status=? where id=?",
                    (cash, "blown" if cash <= a["loss_limit"] else "active", account_id))
    return account(account_id)
