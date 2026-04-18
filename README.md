# Drachmann Trading — Value Investing Dashboard

A Streamlit dashboard for Danish stocks (Nasdaq Copenhagen) built around the
value-investing philosophy of **Jens Løgstrup**: buy quality companies at a
significant discount to intrinsic value, hold for dividends and compounding.

---

## Quick Start

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your Telegram credentials (see below)

# 4. Launch the dashboard
streamlit run app.py
```

On first launch click **Refresh All Data** in the sidebar. This fetches ~45
tickers from yfinance and takes about 2 minutes. All data is cached in a local
SQLite file (`trading_data.db`).

---

## Project Structure

```
drachmann-trading/
├── app.py                  ← Streamlit UI (4 pages)
├── config.py               ← Tickers, thresholds, env vars
├── requirements.txt
├── .env.example            ← Copy to .env and fill in secrets
├── trading_data.db         ← Auto-created SQLite database
└── modules/
    ├── data_fetcher.py     ← yfinance wrapper
    ├── scorer.py           ← Løgstrup Score engine
    ├── database.py         ← SQLite read/write helpers
    ├── telegram_notifier.py← Telegram Bot API calls
    └── scheduler.py        ← Full update pipeline (also cron-runnable)
```

---

## Løgstrup Score Methodology

The score (0–100) is a weighted composite of six value factors:

| Component        | Max pts | Logic                                              |
|------------------|--------:|----------------------------------------------------|
| P/E Ratio        |      25 | < 8 = max; > 25 = 0                               |
| P/B Ratio        |      15 | < 0.8 = max (buying below book); > 3.5 = 0        |
| ROE              |      20 | > 25 % = max; < 5 % = 0                           |
| FCF Yield        |      20 | > 10 % = max; negative = 0                        |
| Dividend Yield   |      10 | > 6 % = max; no dividend = 2                      |
| Debt / Equity    |      10 | < 20 % = max (very low debt); > 150 % = 0         |

**Signals generated automatically:**

| Signal       | Trigger                               |
|--------------|---------------------------------------|
| 🚀 STRONG BUY | Score ≥ 80                           |
| ✅ BUY        | Score ≥ 70                           |
| ⏸ HOLD       | 30 < Score < 70                      |
| 🔴 SELL       | Score ≤ 30 or score dropped ≥ 15 pts |

---

## Setting Up Telegram Alerts

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`, follow the prompts, copy the **token**
3. Send any message to your new bot
4. Open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
5. Copy the `"id"` value from `"chat"` — that is your **Chat ID**
6. Add both values to `.env`:

```
TELEGRAM_TOKEN=110201543:AAHdqTcvCH1vGWJxfSeofSs4tDqQLz...
TELEGRAM_CHAT_ID=123456789
```

7. In the app go to **⚙️ Settings** → click **Test Telegram Connection**

---

## Automated Daily Updates (Cron)

```bash
# Run every weekday at 08:00 (Copenhagen market opens at 09:00 CET)
crontab -e

# Paste (adjust paths):
0 8 * * 1-5 cd /full/path/to/drachmann-trading && /full/path/to/python modules/scheduler.py >> logs/cron.log 2>&1
```

Or run a one-off update from the terminal:

```bash
python modules/scheduler.py
```

---

## Adding / Removing Tickers

Edit `config.py` — the `C25_TICKERS` and `MIDCAP_TICKERS` lists.
All Danish tickers end in `.CO` (Nasdaq Copenhagen).
Run **Refresh All Data** in the app after any change.

---

## Notes & Limitations

* yfinance data quality varies by ticker. Smaller MidCap stocks may have
  incomplete fundamentals; those components score 0 (conservative default).
* Danish financial-sector stocks (banks, insurance) have structurally higher
  D/E ratios — the score will underrate them on that factor.
* This tool is for informational and educational purposes only. It is **not**
  financial advice.
