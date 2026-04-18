"""
Scheduled data-update pipeline.

Can be run directly:
    python modules/scheduler.py

Or via cron (weekdays at 08:00 Copenhagen time):
    0 8 * * 1-5 cd /path/to/project && python modules/scheduler.py
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config
from modules.data_fetcher import fetch_all_stocks
from modules.scorer import calculate_logstrup_score, determine_signal, format_signal_message
from modules.database import (
    initialize_db, save_score, save_signal,
    get_previous_score, mark_signal_sent,
)
from modules.telegram_notifier import send_signal_alert

logger = logging.getLogger(__name__)


def run_update(tickers=None, send_telegram: bool = True):
    """
    Full pipeline:
      1. Fetch fundamental data from yfinance
      2. Compute Løgstrup score for each ticker
      3. Persist scores to SQLite
      4. Generate and (optionally) send Telegram signals
    Returns list of generated signal dicts.
    """
    initialize_db()

    if tickers is None:
        tickers = config.ALL_TICKERS

    logger.info("Starting update for %d tickers …", len(tickers))
    raw_data = fetch_all_stocks(tickers)

    signals_generated = []

    for stock in raw_data:
        ticker = stock["ticker"]

        # Fill sector from config if yfinance didn't return one
        if not stock.get("sector"):
            stock["sector"] = config.SECTOR_MAP.get(ticker)

        # Score
        result = calculate_logstrup_score(stock)
        score = result["total"]
        stock["score"] = score

        # Signal
        previous = get_previous_score(ticker)
        signal = determine_signal(score, previous)
        stock["signal"] = signal

        # Persist
        save_score(ticker, stock)

        # Notify on actionable signals
        if signal in ("BUY", "STRONG BUY", "SELL"):
            company = stock.get("company_name", ticker)
            msg = format_signal_message(ticker, company, score, previous, signal)
            signal_id = save_signal(ticker, company, signal, score, previous, msg)

            if send_telegram:
                ok, _ = send_signal_alert(msg)
                if ok:
                    mark_signal_sent(signal_id)

            signals_generated.append({"ticker": ticker, "signal": signal, "score": score})
            logger.info("%s → %s (%.0f)", ticker, signal, score)

    logger.info("Update complete — %d signals generated.", len(signals_generated))
    return signals_generated


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    run_update(send_telegram=True)
