"""HTTP API + the web app.  uv run uvicorn algotrader.api:app --reload"""
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import data, engine, paper
from .strategy import PRESETS, Strategy

app = FastAPI(title="AlgoTrader", version="2.0.0a1")
MAX_UPLOAD = 50 * 1024 * 1024


@app.exception_handler(ValueError)
async def user_error(_: Request, e: ValueError):
    return JSONResponse({"detail": str(e)}, status_code=400)


@app.get("/api/presets")
def presets():
    return list(PRESETS.values())


@app.get("/api/datasets")
def datasets():
    return data.datasets()


@app.post("/api/backtest")
def backtest(s: Strategy):
    return engine.run(s)


@app.get("/api/candles")
def candles(symbol: str, timeframe: str = "1D", start: str | None = None, end: str | None = None, limit: int = 20000):
    df = data.bars(symbol, timeframe)
    if start:
        df = df[df.index >= pd.Timestamp(start)]
    if end:
        df = df[df.index < pd.Timestamp(end) + pd.Timedelta(days=1)]
    df = df.iloc[:min(limit, 50000)]
    return [{"time": int(t.timestamp()), "iso": str(t), "open": r.open, "high": r.high, "low": r.low, "close": r.close}
            for t, r in zip(df.index, df.itertuples())]


@app.get("/api/sessions")
def sessions(symbol: str = "NIFTY"):
    """Trading days available for Replay."""
    return [str(d) for d in sorted(set(data.load(symbol).index.date))]


@app.post("/api/upload")
async def upload(symbol: str = Form(...), file: UploadFile = File(...)):
    raw = await file.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(413, "File too large (50 MB max)")
    return {"symbol": data.save_upload(symbol, raw)}


class ChatIn(BaseModel):
    messages: list[dict]
    strategy: Strategy | None = None


@app.post("/api/chat")
def chat_turn(body: ChatIn):
    from .chat import chat
    return chat(body.messages, body.strategy)


class AccountIn(BaseModel):
    name: str = "Paper account"
    capital: float = 100_000
    max_loss_pct: float = 20


class TradeIn(BaseModel):
    symbol: str
    timeframe: str
    side: str
    qty: int
    entry_time: str
    exit_time: str
    note: str = ""


@app.get("/api/paper/accounts")
def list_accounts():
    return paper.accounts()


@app.post("/api/paper/accounts")
def new_account(a: AccountIn):
    return paper.create_account(a.name, a.capital, a.max_loss_pct)


@app.get("/api/paper/accounts/{account_id}")
def get_account(account_id: int):
    return paper.account(account_id)


@app.post("/api/paper/accounts/{account_id}/trades")
def add_trade(account_id: int, t: TradeIn):
    return paper.record_trade(account_id, **t.model_dump())


@app.get("/api/portfolio/brokers")
def brokers():
    # ponytail: stub list. Real connectors go through OpenAlgo's API (docs/PLAN.md, phase 3).
    names = ["Zerodha", "Upstox", "Angel One", "Dhan", "Groww", "Fyers", "ICICI Direct", "5paisa"]
    return [{"name": n, "status": "coming soon"} for n in names]


app.mount("/", StaticFiles(directory=Path(__file__).parent / "web", html=True), name="web")
