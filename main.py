"""
XAUUSD AI DERIV BOT - Super Premium Multi-Timeframe
Mengambil H4, H1, M30, M15 dan menganalisis dengan indikator lengkap.
Sinyal hanya jika skor >= 80 dan semua filter terpenuhi.
Mode manual (tidak eksekusi order otomatis).
"""

import time
import logging
import requests
import pandas as pd
from datetime import datetime, time as dt_time

from config.settings import (
    validate_basic_config, is_trading_day, LOG_LEVEL,
    SYMBOL, APP_ID, GRANULARITY_H4, GRANULARITY_H1, GRANULARITY_M30, GRANULARITY_M15,
    CANDLE_COUNT, ACCOUNT_BALANCE, MAX_RETRIES, RETRY_DELAY,
    HTTP_TIMEOUT, SEND_STARTUP_NOTIFICATION, MIN_SCORE,
    LONDON_OPEN_HOUR, LONDON_CLOSE_HOUR, NY_OPEN_HOUR, NY_CLOSE_HOUR,
    MIN_ATR_VOLATILITY, ENABLE_SESSION_FILTER
)

from strategy.indicators import add_all_indicators
from strategy.candlestick_patterns import detect_patterns
from strategy.multi_timeframe import analyze_h4_h1
from strategy.m15_setup import evaluate_m15_setup
from strategy.dynamic_tp import calculate_dynamic_tp
from ai.analyzer import calculate_signal_score
from risk.engine import validate_risk
from risk.position_size import calculate_position_size
from telegram.anti_spam import check_anti_spam
from telegram.bot import send_signal_notification, send_error_notification
from telegram.notifier import send_telegram_message
from database.journal import log_signal_to_db, init_db

# Setup logging
LOG_FILE = "bot_runner.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("XAUUSD_BOT")


def safe_telegram_send(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Gagal mengirim notifikasi Telegram: {e}")
        return False


def fetch_deriv_candles_http(granularity, count=CANDLE_COUNT, retries=MAX_RETRIES):
    url = "https://api.deriv.com/v3/ticks_history"
    params = {
        "ticks_history": SYMBOL,
        "adjust_start_time": 1,
        "count": count,
        "end": "latest",
        "granularity": granularity,
        "style": "candles",
        "app_id": APP_ID
    }
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Mengambil data {granularity}s (percobaan {attempt}/{retries})...")
            response = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise Exception(f"API error: {data['error']}")
            candles = data.get("candles", [])
            if not candles:
                raise Exception("Data candles kosong")
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['epoch'], unit='s')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            if df.isnull().any().any() or (df[['open', 'high', 'low', 'close']] <= 0).any().any():
                raise Exception("Data tidak valid")
            logger.info(f"Berhasil mengambil {len(df)} candle {granularity}s")
            return df
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout (percobaan {attempt})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error: {e} (percobaan {attempt})")
        except Exception as e:
            logger.warning(f"Error: {e} (percobaan {attempt})")
        if attempt < retries:
            time.sleep(RETRY_DELAY)
    logger.error(f"Gagal mengambil data {granularity}s setelah {retries} percobaan")
    return pd.DataFrame()


def is_market_session():
    if not ENABLE_SESSION_FILTER:
        return True   # Bot aktif di semua sesi
    now = datetime.utcnow()
    current_time = now.time()
    london = dt_time(LONDON_OPEN_HOUR, 0) <= current_time <= dt_time(LONDON_CLOSE_HOUR, 0)
    new_york = dt_time(NY_OPEN_HOUR, 0) <= current_time <= dt_time(NY_CLOSE_HOUR, 0)
    return london or new_york


def main():
    logger.info("=" * 50)
    logger.info("XAUUSD AI DERIV BOT - SUPER PREMIUM")
    logger.info("=" * 50)

    try:
        init_db()
        logger.info("Database siap")

        ok, msg = validate_basic_config()
        if not ok:
            err_txt = f"Error Konfigurasi Dasar: {msg}"
            logger.error(err_txt)
            safe_telegram_send(send_error_notification, err_txt)
            return

        if not is_trading_day():
            logger.info("Hari ini akhir pekan. Bot OFF.")
            return
        if not is_market_session():
            logger.info("Di luar sesi pasar London/NY. Bot OFF.")
            return

        # Ambil data multi-timeframe
        df_h4 = fetch_deriv_candles_http(GRANULARITY_H4)
        df_h1 = fetch_deriv_candles_http(GRANULARITY_H1)
        df_m30 = fetch_deriv_candles_http(GRANULARITY_M30)
        df_m15 = fetch_deriv_candles_http(GRANULARITY_M15)

        if any(df.empty for df in [df_h4, df_h1, df_m30, df_m15]):
            err_txt = "Gagal mendapatkan data pasar (salah satu timeframe kosong)."
            logger.error(err_txt)
            safe_telegram_send(send_error_notification, err_txt)
            return

        # Tambahkan indikator ke semua timeframe
        df_h4 = add_all_indicators(df_h4)
        df_h1 = add_all_indicators(df_h1)
        df_m30 = add_all_indicators(df_m30)
        df_m15 = add_all_indicators(df_m15)

        latest_price = df_m15.iloc[-1]['close']
        latest_time = df_m15.iloc[-1]['time']
        logger.info(f"Harga XAUUSD real-time: {latest_price} pada {latest_time}")

        if SEND_STARTUP_NOTIFICATION:
            startup_msg = (
                "🚀 **XAUUSD BOT SUPER PREMIUM AKTIF**\n"
                "=========================\n"
                f"🔹 Harga: `{latest_price}`\n"
                f"🔹 Waktu: `{latest_time}`\n"
                "🔹 Mode: Analisis Multi-Timeframe (H4/H1/M30/M15)"
            )
            safe_telegram_send(send_telegram_message, startup_msg)

        # Analisis tren besar
        logger.info("Analisis tren H4 & H1...")
        higher_tf = analyze_h4_h1(df_h4, df_h1)
        logger.info(f"Bias H4/H1: {higher_tf.get('bias')} | Kekuatan: {higher_tf.get('strength')}")

        # Analisis M30
        logger.info("Analisis M30...")
        m30_context = {
            "bias": higher_tf.get("bias"),
            "structure": higher_tf.get("structure"),
            "adx": higher_tf.get("adx"),
            "rsi": higher_tf.get("rsi"),
            "ema20": df_m30.iloc[-1]['ema20'],
            "ema50": df_m30.iloc[-1]['ema50'],
            "macd_hist": df_m30.iloc[-1]['macd_hist'],
        }

        # Deteksi pola candlestick di M15
        logger.info("Deteksi pola candlestick M15...")
        patterns = detect_patterns(df_m15)

        # Evaluasi setup M15 dengan konfirmasi pola
        logger.info("Evaluasi setup M15...")
        m15_setup = evaluate_m15_setup(df_m15, m30_context, patterns)
        logger.info(f"M15 Signal: {m15_setup.get('signal')} | Reason: {m15_setup.get('reason')}")

        # Hitung skor sinyal
        signal_score = calculate_signal_score(m30_context, m15_setup, higher_tf)
        action = signal_score.get("action", "WAIT")
        score = signal_score.get("score", 0)
        logger.info(f"Signal Score: {score} | Action: {action}")

        if action not in ["BUY", "SELL"] or score < MIN_SCORE:
            logger.info(f"Skor {score} di bawah minimum {MIN_SCORE}. Tidak ada sinyal.")
            return

        # Hitung TP/SL
        current_price = df_m15.iloc[-1]['close']
        tp_sl_data = calculate_dynamic_tp(action, current_price, df_m15)
        signal_payload = {
            "entry": current_price,
            "tp": tp_sl_data.get("tp"),
            "sl": tp_sl_data.get("sl"),
            "pips": tp_sl_data.get("pips"),
            "atr": tp_sl_data.get("atr")
        }

        if signal_payload["tp"] is None or signal_payload["sl"] is None:
            logger.error("TP/SL tidak terdefinisi")
            return

        # Validasi TP/SL
        if action == "BUY":
            if not (signal_payload["tp"] > current_price > signal_payload["sl"]):
                logger.error("TP/SL tidak valid untuk BUY")
                return
        else:
            if not (signal_payload["tp"] < current_price < signal_payload["sl"]):
                logger.error("TP/SL tidak valid untuk SELL")
                return

        # Validasi risiko
        is_risk_ok, risk_msg = validate_risk(signal_payload, action)
        if not is_risk_ok:
            logger.warning(f"Sinyal ditolak Risk Engine: {risk_msg}")
            safe_telegram_send(send_error_notification, f"Sinyal ditolak: {risk_msg}")
            return

        # Anti-spam
        if not check_anti_spam(action, current_price):
            logger.info("Sinyal dicegah oleh Anti-Spam (cooldown aktif).")
            return

        # Hitung ukuran posisi
        risk_calc = calculate_position_size(ACCOUNT_BALANCE, current_price, signal_payload["sl"])
        logger.info(f"Ukuran posisi: {risk_calc}")

        # Catat ke database dan kirim notifikasi
        logger.info("Mengirim notifikasi & mencatat sinyal...")
        log_signal_to_db(signal_payload, action, score, risk_calc)
        safe_telegram_send(send_signal_notification, signal_payload, action, score, risk_calc, m30_context, higher_tf, patterns)

        logger.info("Pipeline selesai.")

    except Exception as e:
        error_msg = f"Critical Error: {str(e)}"
        logger.exception(error_msg)
        safe_telegram_send(send_error_notification, error_msg)


if __name__ == "__main__":
    main()
