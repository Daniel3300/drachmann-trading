"""
Central configuration for Drachmann Trading.
All thresholds and ticker lists are controlled here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Signal Thresholds ─────────────────────────────────────────────────────────
STRONG_BUY_THRESHOLD = int(os.getenv("STRONG_BUY_THRESHOLD", "80"))
BUY_THRESHOLD = int(os.getenv("BUY_THRESHOLD", "70"))
SELL_THRESHOLD = int(os.getenv("SELL_THRESHOLD", "30"))

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "trading_data.db")

# ── Nasdaq Copenhagen — C25 Index ─────────────────────────────────────────────
C25_TICKERS = [
    "NOVO-B.CO",   # Novo Nordisk B
    "MAERSK-B.CO", # A.P. Møller-Mærsk B
    "DSV.CO",      # DSV
    "ORSTED.CO",   # Ørsted
    "CARL-B.CO",   # Carlsberg B
    "COLO-B.CO",   # Coloplast B
    "GMAB.CO",     # Genmab
    "PNDORA.CO",   # Pandora
    "TRYG.CO",     # Tryg
    "DEMANT.CO",   # William Demant
    "FLS.CO",      # FLSmidth & Co.
    "GN.CO",       # GN Store Nord
    "ISS.CO",      # ISS
    "NZYM-B.CO",   # Novozymes B
    "ROCK-B.CO",   # Rockwool B
    "RBREW.CO",    # Royal Unibrew
    "VWS.CO",      # Vestas Wind Systems
    "AMBU-B.CO",   # Ambu B
    "ALK-B.CO",    # ALK-Abelló B
    "NDA-DK.CO",   # Nordea Bank DK
    "JYSK.CO",     # Jyske Bank
    "SCHO.CO",     # Schouw & Co.
    "SYDB.CO",     # Sydbank
    "BAVAR.CO",    # Bavarian Nordic
    "NSIS-B.CO",   # Novonesis B (Novozymes + Chr. Hansen)
]

# ── Nasdaq Copenhagen — MidCap ────────────────────────────────────────────────
MIDCAP_TICKERS = [
    "TIVOLI.CO",   # Tivoli
    "RTX.CO",      # RTX A/S
    "SPNO.CO",     # Sparekassen Sjælland-Fyn
    "RINGK.CO",    # Ringkjøbing Landbobank
    "THYB.CO",     # Thy
    "HMN.CO",      # H. Lundbeck
    "HVID.CO",     # Hvidbjerg Bank
    "HARB-B.CO",   # Harboe Bryggeri B
    "EAC.CO",      # East Asiatic Company
    "GPH.CO",      # GPH
    "NTG.CO",      # NTG Nordic Transport Group
    "SANI.CO",     # Sanistål
    "WDH.CO",      # Wristband
    "HLUN-B.CO",   # H. Lundbeck B
    "NIORD.CO",    # Niord
    "AURI-B.CO",   # Auriga Industries B
    "FFARMS.CO",   # Fjord Seafood/Nordic Aquafarms
    "GRIF.CO",     # Grif Holding
    "VGN.CO",      # Vestjysk Bank
]

ALL_TICKERS = C25_TICKERS + MIDCAP_TICKERS

# ── Sector Map (fallback if yfinance does not return sector) ──────────────────
SECTOR_MAP = {
    "NOVO-B.CO":   "Healthcare",
    "MAERSK-B.CO": "Industrials",
    "DSV.CO":      "Industrials",
    "ORSTED.CO":   "Utilities",
    "CARL-B.CO":   "Consumer Staples",
    "COLO-B.CO":   "Healthcare",
    "GMAB.CO":     "Healthcare",
    "PNDORA.CO":   "Consumer Discretionary",
    "TRYG.CO":     "Financials",
    "DEMANT.CO":   "Healthcare",
    "FLS.CO":      "Industrials",
    "GN.CO":       "Technology",
    "ISS.CO":      "Industrials",
    "NZYM-B.CO":   "Basic Materials",
    "ROCK-B.CO":   "Basic Materials",
    "RBREW.CO":    "Consumer Staples",
    "VWS.CO":      "Utilities",
    "AMBU-B.CO":   "Healthcare",
    "ALK-B.CO":    "Healthcare",
    "NDA-DK.CO":   "Financials",
    "JYSK.CO":     "Financials",
    "SCHO.CO":     "Industrials",
    "SYDB.CO":     "Financials",
    "BAVAR.CO":    "Healthcare",
    "NSIS-B.CO":   "Basic Materials",
    "TIVOLI.CO":   "Consumer Discretionary",
    "RTX.CO":      "Technology",
    "SPNO.CO":     "Financials",
    "RINGK.CO":    "Financials",
    "THYB.CO":     "Financials",
    "HMN.CO":      "Healthcare",
    "HVID.CO":     "Financials",
    "HARB-B.CO":   "Consumer Staples",
    "EAC.CO":      "Consumer Staples",
    "NTG.CO":      "Industrials",
    "SANI.CO":     "Industrials",
    "VGN.CO":      "Financials",
}
