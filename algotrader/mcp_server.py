"""MCP server: lets any MCP client (Claude, Cursor, your own bot) list data and backtest strategies.

    uv run python -m algotrader.mcp_server            # stdio, for Claude Desktop / Claude Code
    uv run python -m algotrader.mcp_server --http     # streamable HTTP on :8001/mcp
"""
import sys

from mcp.server.mcpserver import MCPServer

from . import data, engine
from .strategy import PRESETS, Strategy

mcp = MCPServer("algotrader", instructions=(
    "Backtest trading strategies on Indian market data. Call strategy_schema to see the rule format, "
    "list_datasets for symbols, then run_backtest. Results include real Indian charges and slippage."))


@mcp.tool()
def list_datasets() -> list[dict]:
    """Symbols with their date range and supported timeframes."""
    return data.datasets()


@mcp.tool()
def list_presets() -> list[dict]:
    """Ready-made strategies you can run as-is or tweak."""
    return [p.model_dump() for p in PRESETS.values()]


@mcp.tool()
def strategy_schema() -> dict:
    """JSON schema of a strategy. Terms: numbers, open/high/low/close/volume, or indicators like sma(50), ema(20),
    rsi(14), bb_upper(20,2), bb_lower(20,2), bb_mid(20,2), macd(12,26,9), macd_signal(12,26,9), atr(14),
    highest(20), lowest(20), pct_change(1), gap_pct, supertrend(10,3). Ops: < > <= >= crosses_above crosses_below."""
    return Strategy.model_json_schema()


@mcp.tool()
def run_backtest(strategy: dict) -> dict:
    """Backtest a strategy (see strategy_schema). Returns metrics, coaching insights and the trade list."""
    s = Strategy.model_validate(strategy)
    if s.kind == "code":
        raise ValueError("Code strategies can't be run over MCP; use rules.")
    r = engine.run(s)
    return {"metrics": r["metrics"], "insights": r["insights"], "trades": r["trades"][-50:],
            "trades_total": len(r["trades"])}


if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run("streamable-http", port=8001)
    else:
        mcp.run()
