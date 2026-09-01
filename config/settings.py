import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def _get_env(key: str, default: str = "") -> str:
    """Ambil env var, jika kosong atau None kembalikan default."""
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return default
    return value


def _get_env_int(key: str, default: int) -> int:
    """Ambil env var sebagai integer, fallback ke default jika kosong/invalid."""
    raw = _get_env(key, str(default))
    try:
        return int(raw)
    except (ValueError, TypeError):
        return default


def _get_env_float(key: str, default: float) -> float:
    """Ambil env var sebagai float, fallback ke default jika kosong/invalid."""
    raw = _get_env(key, str(default))
    try:
        return float(raw)
    except (ValueError, TypeError):
        return default


def _get_env_bool(key: str, default: bool) -> bool:
    """Ambil env var sebagai boolean, fallback ke default jika kosong/invalid."""
    raw = _get_env(key, str(default)).lower()
    if raw in ("true", "1", "yes"):
        return True
    elif raw in ("false", "0", "no"):
        return False
    return default


# ================== KONFIGURASI UTAMA ==================
SYMBOL = _get_env("SYMBOL", "frxXAUUSD")
APP_ID = _get_env("APP_ID", "1089")

# Timeframes (dalam detik)
GRANULARITY_H4 = _get_env_int("GRANULARITY_H4", 14400)
GRANULARITY_H1 = _get_env_int("GRANULARITY_H1", 3600)
GRANULARITY_M30 = _get_env_int("GRANULARITY_M30", 1800)
GRANULARITY_M15 = _get_env_int("GRANULARITY_M15", 900)

CANDLE_COUNT = _get_env_int("CANDLE_COUNT", 200)
ACCOUNT_BALANCE = _get_env_float("ACCOUNT_BALANCE", 10000.0)
MAX_RETRIES = _get_env_int("MAX_RETRIES", 3)
RETRY_DELAY = _get_env_int("RETRY_DELAY", 5)
HTTP_TIMEOUT = _get_env_int("HTTP_TIMEOUT", 10)
SEND_STARTUP_NOTIFICATION = _get_env_bool("SEND_STARTUP_NOTIFICATION", True)
MIN_SCORE = _get_env_float("MIN_SCORE", 80.0)

# Filter sesi pasar (UTC)
LONDON_OPEN_HOUR = _get_env_int("LONDON_OPEN_HOUR", 8)
LONDON_CLOSE_HOUR = _get_env_int("LONDON_CLOSE_HOUR", 16)
NY_OPEN_HOUR = _get_env_int("NY_OPEN_HOUR", 13)
NY_CLOSE_HOUR = _get_env_int("NY_CLOSE_HOUR", 21)

# Volatilitas minimum (ATR)
MIN_ATR_VOLATILITY = _get_env_float("MIN_ATR_VOLATILITY", 2.5)

# Telegram
TELEGRAM_BOT_TOKEN = _get_env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = _get_env("TELEGRAM_CHAT_ID", "")

# Logging
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")


def validate_basic_config():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False, "TELEGRAM_BOT_TOKEN atau TELEGRAM_CHAT_ID belum diatur"
    if ACCOUNT_BALANCE <= 0:
        return False, "ACCOUNT_BALANCE harus > 0"
    if MIN_SCORE < 0 or MIN_SCORE > 100:
        return False, "MIN_SCORE harus antara 0-100"
    return True, "OK"


def is_trading_day():
    return datetime.now().weekday() < 5
