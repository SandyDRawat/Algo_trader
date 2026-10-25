"""The engine is the money path: these pin down fills, stops, shorts, costs and warm-up."""
import pandas as pd
import pytest

from algotrader import costs, engine
from algotrader.strategy import Condition, Strategy


def bars(rows):
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="D")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx).assign(volume=0.0)


FLAT = [(100, 101, 99, 100)] * 3


def strat(**kw):
    return Strategy(symbol="TEST", slippage_pct=0, **kw)


@pytest.fixture(autouse=True)
def no_costs(monkeypatch):
    monkeypatch.setattr(engine, "charges", lambda *a: 0.0)


def test_fills_next_bar_open_not_signal_close():
    df = bars([(100, 101, 99, 100), (110, 111, 109, 110), (120, 121, 119, 120)])
    s = strat(entry=[Condition(left="close", op=">=", right=100)], capital=1000)
    tr = engine.run(s, df)["trades"][0]
    assert tr["entry_time"].startswith("2024-01-02") and tr["entry_price"] == 110  # signal on day 1 close, fill day 2 open


def test_stop_fills_at_open_when_price_gaps_through():
    df = bars([*FLAT, (100, 100, 100, 100), (80, 82, 78, 81)])
    s = strat(entry=[Condition(left="close", op=">=", right=100)], stop_loss_pct=5, capital=1000)
    tr = engine.run(s, df)["trades"][0]
    assert tr["reason"] == "stop" and tr["exit_price"] == 80  # gapped below 95, so the open, not 95


def test_stop_wins_when_stop_and_target_hit_same_bar():
    df = bars([*FLAT, (100, 120, 80, 100)])
    s = strat(entry=[Condition(left="close", op=">=", right=100)], stop_loss_pct=5, take_profit_pct=5, capital=1000)
    assert engine.run(s, df)["trades"][0]["reason"] == "stop"


def test_short_profits_when_price_falls():
    df = bars([(100, 100, 100, 100), (100, 100, 100, 100), (90, 90, 90, 90)])
    s = strat(entry=[Condition(left="close", op=">=", right=100)], direction="short", capital=1000, segment="futures")
    r = engine.run(s, df)
    assert r["trades"][0]["pnl"] == 100  # 10 units × ₹10
    assert r["metrics"]["final_equity"] == 1100


def test_costs_reduce_equity(monkeypatch):
    monkeypatch.setattr(engine, "charges", costs.charges)
    df = bars([*FLAT, (100, 100, 100, 100)])
    s = strat(entry=[Condition(left="close", op=">=", right=100)], capital=100_000)
    m = engine.run(s, df)["metrics"]
    assert 0 < m["costs"] and m["final_equity"] == pytest.approx(100_000 - m["costs"], abs=0.01)


def test_indicators_warm_up_before_window():
    rows = [(100 + i, 101 + i, 99 + i, 100 + i) for i in range(30)]
    s = strat(entry=[Condition(left="close", op=">", right="sma(20)")], start="2024-01-25", capital=10_000)
    assert engine.run(s, bars(rows))["trades"][0]["entry_time"].startswith("2024-01-26")  # sma(20) valid on day 1 of window


def test_delivery_charges_match_contract_note():
    # ₹1,00,000 delivery buy: STT 100 + exchange 2.97 + SEBI 0.10 + stamp 15 + GST on (2.97 + 0.10)
    assert costs.charges("equity_delivery", "buy", 1000, 100) == pytest.approx(118.62, abs=0.01)
