"""
Telegram notification layer — uses the Bot API directly via requests.
No external telegram library needed; just python-requests.
"""

import logging
import requests

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

_BASE = "https://api.telegram.org/bot{token}/{method}"


def _post(method: str, payload: dict) -> tuple[bool, str]:
    """Low-level POST to Telegram Bot API. Returns (success, message)."""
    token = config.TELEGRAM_TOKEN
    if not token:
        return False, "TELEGRAM_TOKEN is not set in .env"

    try:
        url = _BASE.format(token=token, method=method)
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if data.get("ok"):
            return True, "OK"
        return False, data.get("description", "Unknown Telegram API error")
    except requests.exceptions.Timeout:
        return False, "Request timed out — check your internet connection"
    except requests.exceptions.ConnectionError:
        return False, "Network error — cannot reach Telegram"
    except Exception as exc:
        return False, str(exc)


def send_message(text: str, parse_mode: str = "Markdown") -> tuple[bool, str]:
    """Send a text message to the configured chat."""
    chat_id = config.TELEGRAM_CHAT_ID
    if not chat_id:
        return False, "TELEGRAM_CHAT_ID is not set in .env"

    ok, msg = _post("sendMessage", {
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": parse_mode,
    })
    if ok:
        logger.info("Telegram message sent.")
    else:
        logger.error("Telegram send failed: %s", msg)
    return ok, msg


def test_connection() -> tuple[bool, str]:
    """Verify bot credentials by sending a test message."""
    return send_message(
        "🤖 *Drachmann Trading Bot* — Connection test successful\\!\n"
        "_Your Løgstrup score alerts are configured correctly\\._",
        parse_mode="MarkdownV2",
    )


def send_signal_alert(message: str) -> tuple[bool, str]:
    return send_message(message, parse_mode="Markdown")
