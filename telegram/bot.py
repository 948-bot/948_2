import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def _send_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

def send_signal_notification(signal_payload, action, score, risk_calc, m30_context, higher_tf, patterns):
    entry = signal_payload.get("entry")
    tp = signal_payload.get("tp")
    sl = signal_payload.get("sl")
    lot = risk_calc.get("lot")
    risk_amount = risk_calc.get("risk_amount")
    atr = signal_payload.get("atr")

    # Format pola yang terdeteksi
    pattern_names = [k for k, v in patterns.items() if v]
    patterns_str = ", ".join(pattern_names) if pattern_names else "Tidak ada"

    text = (
        f"🔥 **SINYAL PREMIUM {action}**\n"
        f"================================\n"
        f"💰 Entry: {entry}\n"
        f"🎯 TP: {tp}\n"
        f"🛑 SL: {sl}\n"
        f"📊 Skor: {score}/100\n"
        f"📈 Tren: {higher_tf.get('bias')} (Kekuatan {higher_tf.get('strength')}%)\n"
        f"📉 ATR: {atr}\n"
        f"🧩 Pola: {patterns_str}\n"
        f"💼 Lot: {lot} (Risiko ${risk_amount})\n"
        f"================================\n"
        f"⏰ {m30_context.get('structure', '')}"
    )
    _send_message(text)

def send_error_notification(error_text: str):
    text = f"⚠️ **Error**\n{error_text}"
    _send_message(text)
