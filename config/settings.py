import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ================== KONFIGURASI UTAMA ==================
SYMBOL = os.getenv("SYMBOL", "frxXAUUSD")
APP_ID = os.getenv("APP_ID", "1089")

# Timeframes (dalam detik)
GRANULARITY_H4 = int(os.getenv("GRANULARITY_H4", 14400))
GRANULARITY_H1 = int(os.getenv("GRANULARITY_H1", 3600))
GRANULARITY_M30 = int(os.getenv("GRANULARITY_M30", 1800))
GRANULARITY_M15 = int(os.getenv("GRANULARITY_M15", 900))

CANDLE_COUNT = int(os.getenv("CANDLE_COUNT", 200))  # Cukup untuk indikator
ACCOUNT_BALANCE = float(os.getenv("ACCOUNT_BALANCE", 10000.0))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 10))
SEND_STARTUP_NOTIFICATION = os.getenv("SEND_STARTUP_NOTIFICATION", "True").lower() == "true"
MIN_SCORE = float(os.getenv("MIN_SCORE", 80.0))

# Filter sesi pasar (UTC)
LONDON_OPEN_HOUR = int(os.getenv("LONDON_OPEN_HOUR", 8))
LONDON_CLOSE_HOUR = int(os.getenv("LONDON_CLOSE_HOUR", 16))
NY_OPEN_HOUR = int(os.getenv("NY_OPEN_HOUR", 13))
NY_CLOSE_HOUR = int(os.getenv("NY_CLOSE_HOUR", 21))

# Volatilitas minimum (ATR)
MIN_ATR_VOLATILITY = float(os.getenv("MIN_ATR_VOLATILITY", 2.5))

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


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
