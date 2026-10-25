"""Strategy chat: plain English in, a filled-in Strategy out (the same spec the form edits)."""
import json
import os

from pydantic import BaseModel, Field

from . import data
from .strategy import PRESETS, Strategy

MODEL = os.environ.get("ALGO_CHAT_MODEL", "claude-opus-5-5")

SYSTEM = """You help Indian retail traders turn trading ideas into testable strategy rules, and you teach as you go.
You are not a financial adviser: never promise returns or recommend real trades.

Each turn, return the COMPLETE current strategy (start from the one given, apply the user's changes) plus a short reply.
Rule terms: numbers; price columns open, high, low, close, volume; indicators sma(n), ema(n), rsi(n), bb_upper(n,k),
bb_lower(n,k), bb_mid(n,k), macd(fast,slow,signal), macd_signal(fast,slow,signal), atr(n), highest(n) (prior n-bar high),
lowest(n), pct_change(n) (in %), gap_pct (opening gap vs previous close, in %), supertrend(n,k).
Ops: < > <= >= crosses_above crosses_below. entry_logic/exit_logic: all = AND, any = OR.
Stops/targets are percentages from the entry price. Timeframes: 1min 5min 15min 1h 1D 1W (intraday needs intraday data).
Segments: equity_delivery (swing/positional), equity_intraday, futures, options. Shorting needs futures or intraday.

If something the idea needs can't be expressed with these terms, say so plainly and offer the nearest version.
If a key detail is missing, pick a sensible default and say what you assumed in one line. Keep replies under 80 words.
Set ready_to_run true when the strategy has at least one entry rule and an exit (rule, stop, target or max_bars)."""


class ChatOut(BaseModel):
    reply: str = Field(description="Short answer to the user, mention any assumptions")
    strategy: Strategy
    ready_to_run: bool


def chat(messages: list[dict], current: Strategy | None):
    try:
        import anthropic
    except ImportError:
        raise ValueError("Chat needs the 'ai' extra: uv sync --extra ai")
    context = json.dumps({
        "current_strategy": (current or Strategy()).model_dump(),
        "datasets": [{k: d[k] for k in ("symbol", "start", "end", "timeframes")} for d in data.datasets()],
        "presets": list(PRESETS),
    })
    turns = [{"role": m["role"], "content": str(m["content"])[:4000]} for m in messages[-20:] if m.get("role") in ("user", "assistant")]
    if not turns or turns[-1]["role"] != "user":
        raise ValueError("Send a message first.")
    turns[-1] = {"role": "user", "content": f"<context>{context}</context>\n\n{turns[-1]['content']}"}
    try:
        client = anthropic.Anthropic()
    except Exception:  # no credentials configured
        raise ValueError("Chat isn't configured: set ANTHROPIC_API_KEY on the server.")
    try:
        resp = client.beta.messages.parse(
            model=MODEL, max_tokens=4000, system=SYSTEM, messages=turns, output_format=ChatOut,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
    except (anthropic.AuthenticationError, TypeError):  # TypeError = SDK found no credentials
        raise ValueError("Chat isn't configured: set ANTHROPIC_API_KEY on the server.")
    except anthropic.APIError as e:
        raise ValueError(f"The assistant is unavailable right now ({type(e).__name__}). Use the form meanwhile.")
    if resp.stop_reason == "refusal" or resp.parsed_output is None:
        raise ValueError("The assistant couldn't help with that one. Try rephrasing the trading idea.")
    return resp.parsed_output.model_dump()
