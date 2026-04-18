"""
yfinance wrapper for Danish stocks.
All monetary fields are returned in the ticker's native currency (usually DKK).
"""

import math
import time
import logging
import yfinance as yf

logger = logging.getLogger(__name__)


def _safe(d: dict, key: str, default=None):
    """Return d[key], substituting default for None / NaN / Inf."""
    val = d.get(key, default)
    if val is None:
        return default
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return default
    return val


def fetch_stock_data(ticker: str, retries: int = 3):
    """
    Fetch fundamental snapshot for one ticker.
    Retries up to `retries` times on rate-limit errors with exponential backoff.
    Returns None if yfinance cannot return a price (delisted / wrong symbol).
    """
    for attempt in range(retries):
        try:
            info = yf.Ticker(ticker).info

            price = _safe(info, "currentPrice") or _safe(info, "regularMarketPrice")
            if price is None:
                logger.warning("No price data for %s — skipping", ticker)
                return None

            market_cap = _safe(info, "marketCap")
            fcf = _safe(info, "freeCashflow")
            fcf_yield = (fcf / market_cap) if (fcf and market_cap and market_cap > 0) else None

            return {
                "ticker":            ticker,
                "company_name":      _safe(info, "longName") or _safe(info, "shortName") or ticker,
                "current_price":     price,
                "currency":          _safe(info, "currency", "DKK"),
                "market_cap":        market_cap,
                "pe":                _safe(info, "trailingPE") or _safe(info, "forwardPE"),
                "pb":                _safe(info, "priceToBook"),
                "peg_ratio":         _safe(info, "pegRatio"),
                "book_value":        _safe(info, "bookValue"),
                "trailing_eps":      _safe(info, "trailingEps"),
                "forward_eps":       _safe(info, "forwardEps"),
                "roe":               _safe(info, "returnOnEquity"),
                "roa":               _safe(info, "returnOnAssets"),
                "gross_margins":     _safe(info, "grossMargins"),
                "operating_margins": _safe(info, "operatingMargins"),
                "profit_margins":    _safe(info, "profitMargins"),
                "revenue_growth":    _safe(info, "revenueGrowth"),
                "earnings_growth":   _safe(info, "earningsGrowth"),
                "fcf":               fcf,
                "fcf_yield":         fcf_yield,
                "de_ratio":          _safe(info, "debtToEquity"),
                "current_ratio":     _safe(info, "currentRatio"),
                "quick_ratio":       _safe(info, "quickRatio"),
                "total_cash":        _safe(info, "totalCash"),
                "total_debt":        _safe(info, "totalDebt"),
                "div_yield":         _safe(info, "dividendYield"),
                "div_rate":          _safe(info, "dividendRate"),
                "week52_high":       _safe(info, "fiftyTwoWeekHigh"),
                "week52_low":        _safe(info, "fiftyTwoWeekLow"),
                "beta":              _safe(info, "beta"),
                "sector":            _safe(info, "sector"),
                "industry":          _safe(info, "industry"),
                "employees":         _safe(info, "fullTimeEmployees"),
                "description":       _safe(info, "longBusinessSummary"),
            }

        except Exception as exc:
            msg = str(exc)
            if "Too Many Requests" in msg or "rate limit" in msg.lower():
                wait = 2 ** attempt * 3  # 3s, 6s, 12s
                logger.warning("Rate limited on %s — retrying in %ds (attempt %d/%d)",
                               ticker, wait, attempt + 1, retries)
                time.sleep(wait)
            else:
                logger.error("Error fetching %s: %s", ticker, exc)
                return None

    logger.error("Gave up on %s after %d retries", ticker, retries)
    return None


def fetch_price_history(ticker: str, period: str = "1y"):
    """Return an OHLCV DataFrame or None if unavailable."""
    try:
        hist = yf.Ticker(ticker).history(period=period)
        return hist if not hist.empty else None
    except Exception as exc:
        logger.error("History error for %s: %s", ticker, exc)
        return None


def fetch_all_stocks(tickers: list, delay: float = 1.5):
    """
    Fetch fundamental data for a list of tickers.
    Uses a 1.5s delay between requests to stay within yfinance rate limits.
    """
    results = []
    total = len(tickers)
    for i, ticker in enumerate(tickers, 1):
        logger.info("[%d/%d] Fetching %s …", i, total, ticker)
        data = fetch_stock_data(ticker)
        if data:
            results.append(data)
        time.sleep(delay)
    return results
