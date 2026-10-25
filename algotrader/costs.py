"""Indian trading charges per order side. Rates as of Oct 2026 (STT revised 1 Apr 2026).

ponytail: one flat table; these change every budget, so this dict is the calibration
knob, not code. Verify against your broker's contract note before trusting a backtest.
"""
RATES_AS_OF = "2026-10"

# All values are fractions of turnover unless named *_flat.
SEGMENTS = {
    "equity_delivery": dict(brokerage_pct=0.0, brokerage_cap=0, stt_buy=0.001, stt_sell=0.001,
                            exchange=0.0000297, stamp_buy=0.00015),
    "equity_intraday": dict(brokerage_pct=0.0003, brokerage_cap=20, stt_buy=0.0, stt_sell=0.00025,
                            exchange=0.0000297, stamp_buy=0.00003),
    "futures": dict(brokerage_pct=0.0003, brokerage_cap=20, stt_buy=0.0, stt_sell=0.0005,
                    exchange=0.0000173, stamp_buy=0.00002),
    "options": dict(brokerage_flat=20, stt_buy=0.0, stt_sell=0.0015,
                    exchange=0.0003503, stamp_buy=0.00003),  # on premium turnover
}
SEBI_FEE = 0.000001  # ₹10 per crore
GST = 0.18           # on brokerage + exchange + SEBI fee


def charges(segment, side, price, qty):
    """Total rupees charged for one order. side is 'buy' or 'sell'."""
    r = SEGMENTS[segment]
    turnover = price * qty
    brokerage = r.get("brokerage_flat") or min(turnover * r.get("brokerage_pct", 0), r.get("brokerage_cap", 0))
    stt = turnover * r["stt_buy" if side == "buy" else "stt_sell"]
    exchange = turnover * r["exchange"]
    sebi = turnover * SEBI_FEE
    stamp = turnover * r["stamp_buy"] if side == "buy" else 0.0
    return brokerage + stt + exchange + sebi + stamp + GST * (brokerage + exchange + sebi)
