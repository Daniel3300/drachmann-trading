"""
Løgstrup Score engine (0–100).

Jens Løgstrup's philosophy distilled into six weighted components:
  1. P/E  — buying earnings cheaply             (25 pts)
  2. P/B  — "buying 1 DKK for 50 øre"           (15 pts)
  3. ROE  — management quality / compounding    (20 pts)
  4. FCF  — real cash, not accounting fiction   (20 pts)
  5. Div  — tangible shareholder return         (10 pts)
  6. D/E  — balance-sheet safety margin         (10 pts)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def calculate_logstrup_score(data: dict) -> dict:
    """
    Returns {"total": float, "components": {name: {"score": n, "value": v, "unit": u}}}.
    Components with missing data score 0 — conservative by design.
    """
    if not data:
        return {"total": 0, "components": {}}

    score = 0
    components = {}

    # ── 1. P/E (25 pts) ───────────────────────────────────────────────────────
    pe = data.get("pe")
    pe_score = 0
    if pe and pe > 0:
        if   pe < 8:   pe_score = 25
        elif pe < 12:  pe_score = 20
        elif pe < 15:  pe_score = 15
        elif pe < 20:  pe_score = 10
        elif pe < 25:  pe_score = 5
    components["P/E Ratio"] = {"score": pe_score, "value": pe, "unit": "x", "max": 25}
    score += pe_score

    # ── 2. P/B (15 pts) ───────────────────────────────────────────────────────
    pb = data.get("pb")
    pb_score = 0
    if pb and pb > 0:
        if   pb < 0.8:  pb_score = 15
        elif pb < 1.2:  pb_score = 12
        elif pb < 1.8:  pb_score = 8
        elif pb < 2.5:  pb_score = 4
        elif pb < 3.5:  pb_score = 2
    components["P/B Ratio"] = {"score": pb_score, "value": pb, "unit": "x", "max": 15}
    score += pb_score

    # ── 3. ROE (20 pts) ───────────────────────────────────────────────────────
    # yfinance returns decimal (0.18 = 18 %). Negative ROE scores 0.
    roe = data.get("roe")
    roe_score = 0
    roe_pct = None
    if roe is not None:
        roe_pct = roe * 100
        if   roe_pct > 25: roe_score = 20
        elif roe_pct > 20: roe_score = 16
        elif roe_pct > 15: roe_score = 12
        elif roe_pct > 10: roe_score = 8
        elif roe_pct > 5:  roe_score = 4
    components["ROE"] = {"score": roe_score, "value": roe_pct, "unit": "%", "max": 20}
    score += roe_score

    # ── 4. FCF Yield (20 pts) ─────────────────────────────────────────────────
    fcf_yield = data.get("fcf_yield")
    fcf_score = 0
    fcf_pct = None
    if fcf_yield is not None:
        fcf_pct = fcf_yield * 100
        if   fcf_pct > 10: fcf_score = 20
        elif fcf_pct > 7:  fcf_score = 16
        elif fcf_pct > 5:  fcf_score = 12
        elif fcf_pct > 3:  fcf_score = 8
        elif fcf_pct > 0:  fcf_score = 4
    components["FCF Yield"] = {"score": fcf_score, "value": fcf_pct, "unit": "%", "max": 20}
    score += fcf_score

    # ── 5. Dividend Yield (10 pts) ────────────────────────────────────────────
    div_yield = data.get("div_yield")
    div_score = 0
    div_pct = None
    if div_yield and div_yield > 0:
        div_pct = div_yield * 100
        if   div_pct > 6:   div_score = 10
        elif div_pct > 4:   div_score = 8
        elif div_pct > 2.5: div_score = 6
        elif div_pct > 1.5: div_score = 4
        elif div_pct > 0:   div_score = 2
    components["Dividend Yield"] = {"score": div_score, "value": div_pct, "unit": "%", "max": 10}
    score += div_score

    # ── 6. Debt / Equity (10 pts) ─────────────────────────────────────────────
    # yfinance debtToEquity is already in percent (150 = 150 %).
    de = data.get("de_ratio")
    de_score = 0
    if de is not None:
        if   de < 0:    de_score = 0   # negative equity = red flag
        elif de < 20:   de_score = 10
        elif de < 50:   de_score = 8
        elif de < 100:  de_score = 5
        elif de < 150:  de_score = 2
    else:
        de_score = 3   # unknown — slight penalty vs. missing
    components["Debt / Equity"] = {"score": de_score, "value": de, "unit": "pct_raw", "max": 10}
    score += de_score

    return {"total": min(round(score, 1), 100), "components": components}


def determine_signal(score: float, previous_score=None) -> str:
    """Classify a score as STRONG BUY / BUY / HOLD / SELL."""
    if score >= config.STRONG_BUY_THRESHOLD:
        return "STRONG BUY"
    if score >= config.BUY_THRESHOLD:
        return "BUY"
    if score <= config.SELL_THRESHOLD:
        return "SELL"
    if previous_score is not None and (score - previous_score) <= -15:
        return "SELL"   # sharp deterioration — treat as sell signal
    return "HOLD"


def format_signal_message(ticker: str, company: str, score: float,
                           previous_score, signal: str) -> str:
    """Compose a Telegram-ready Markdown message for one signal."""
    emoji = {"STRONG BUY": "🚀", "BUY": "✅", "SELL": "🔴", "HOLD": "⏸️"}.get(signal, "ℹ️")

    change_line = ""
    if previous_score is not None:
        delta = score - previous_score
        arrow = "↑" if delta >= 0 else "↓"
        change_line = f"\nScore change: {arrow} {abs(delta):.1f} pts"

    return (
        f"{emoji} *{signal}* — {company} `({ticker})`\n"
        f"Løgstrup Score: *{score:.0f}/100*{change_line}\n"
        f"_Drachmann Trading Bot — {__import__('datetime').date.today()}_"
    )
