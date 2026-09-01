import logging
import json
from openai import OpenAI
from config.settings import GEMINI_API_KEY

logger = logging.getLogger("GeminiAI")

def analyze_with_gemini(market_data: dict) -> dict:
    if not GEMINI_API_KEY:
        return {"action": "WAIT", "confidence": 0, "reason": "Gemini tidak dikonfigurasi"}

    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    prompt = f"""
Kamu adalah analis trading XAUUSD profesional. Gunakan data teknikal real-time berikut untuk memberikan rekomendasi trading yang akurat dan hindari sinyal palsu.

Data:
- Tren H4/H1: {market_data.get('bias', 'NEUTRAL')} (kekuatan {market_data.get('strength', 0)})
- ADX H4: {market_data.get('adx', 0)}
- RSI H4: {market_data.get('rsi', 0)}
- Setup M15: {market_data.get('m15_signal', 'WAIT')}
- Alasan setup: {market_data.get('m15_reason', '')}
- Pola candlestick: {market_data.get('patterns', '')}

Tugas:
1. Analisis apakah kondisi pasar mendukung BUY, SELL, atau WAIT.
2. Berikan confidence 0-100 yang realistis. Confidence >= 60 hanya jika semua faktor sangat mendukung.
3. Jika ragu atau tidak ada konfirmasi kuat, pilih WAIT.

Jawab HANYA dalam format JSON tanpa penjelasan:
{{"action": "BUY/SELL/WAIT", "confidence": 0-100, "reason": "alasan singkat"}}
"""

    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": "Anda adalah asisten trading profesional yang menghindari sinyal palsu."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150
        )
        content = response.choices[0].message.content.strip()
        # Bersihkan jika ada markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        data = json.loads(content)
        action = data.get("action", "WAIT").upper()
        confidence = float(data.get("confidence", 0))
        reason = data.get("reason", "")
        return {"action": action, "confidence": confidence, "reason": reason}
    except Exception as e:
        logger.error(f"Error Gemini: {e}")
        return {"action": "WAIT", "confidence": 0, "reason": f"Error: {e}"}
