"""
SQLite persistence layer.
Stores daily scores and signal history so the app can display trends.
"""

import sqlite3
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def get_connection():
    return sqlite3.connect(config.DB_PATH, check_same_thread=False)


def initialize_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker          TEXT    NOT NULL,
            company_name    TEXT,
            date            TEXT    NOT NULL,
            score           REAL,
            pe              REAL,
            pb              REAL,
            roe             REAL,
            fcf_yield       REAL,
            div_yield       REAL,
            de_ratio        REAL,
            current_price   REAL,
            market_cap      REAL,
            sector          TEXT,
            signal          TEXT,
            UNIQUE(ticker, date)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS signal_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker          TEXT    NOT NULL,
            company_name    TEXT,
            timestamp       TEXT    NOT NULL,
            signal_type     TEXT    NOT NULL,
            score           REAL,
            previous_score  REAL,
            message         TEXT,
            sent_to_telegram INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def save_score(ticker: str, data: dict):
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        INSERT OR REPLACE INTO scores
            (ticker, company_name, date, score, pe, pb, roe, fcf_yield,
             div_yield, de_ratio, current_price, market_cap, sector, signal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticker,
        data.get("company_name"),
        today,
        data.get("score"),
        data.get("pe"),
        data.get("pb"),
        data.get("roe"),
        data.get("fcf_yield"),
        data.get("div_yield"),
        data.get("de_ratio"),
        data.get("current_price"),
        data.get("market_cap"),
        data.get("sector"),
        data.get("signal"),
    ))

    conn.commit()
    conn.close()


def get_latest_scores() -> pd.DataFrame:
    """Return the most recent score row per ticker."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT s.*
        FROM scores s
        INNER JOIN (
            SELECT ticker, MAX(date) AS max_date
            FROM scores
            GROUP BY ticker
        ) latest ON s.ticker = latest.ticker AND s.date = latest.max_date
        ORDER BY s.score DESC NULLS LAST
    """, conn)
    conn.close()
    return df


def get_score_history(ticker: str, days: int = 90) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT date, score, signal
        FROM scores
        WHERE ticker = ?
          AND date >= date('now', ?)
        ORDER BY date ASC
    """, conn, params=(ticker, f"-{days} days"))
    conn.close()
    return df


def get_previous_score(ticker: str):
    """Return the second-most-recent score for a ticker (used for delta)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT score FROM scores
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT 2
    """, (ticker,))
    rows = cur.fetchall()
    conn.close()
    return rows[1][0] if len(rows) >= 2 else None


def save_signal(ticker, company_name, signal_type, score, previous_score, message) -> int:
    conn = get_connection()
    cur = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO signal_log
            (ticker, company_name, timestamp, signal_type, score, previous_score, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ticker, company_name, ts, signal_type, score, previous_score, message))

    signal_id = cur.lastrowid
    conn.commit()
    conn.close()
    return signal_id


def get_signal_log(limit: int = 100) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM signal_log
        ORDER BY timestamp DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df


def mark_signal_sent(signal_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE signal_log SET sent_to_telegram = 1 WHERE id = ?", (signal_id,))
    conn.commit()
    conn.close()
