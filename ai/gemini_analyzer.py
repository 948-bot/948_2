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
INSTRUKSI UTAMA (ANTI-HALUSINASI & ZERO GUESSED SIGNALS):
Dilarang keras menebak sinyal, berhalusinasi, atau memberikan keputusan berdasarkan kira-kira. Keputusan trading HARUS murni hasil analisis mendalam dari data teknikal real-time di bawah ini. Jika data tidak meyakinkan atau ragu-ragu, WAJIB hukumnya untuk memilih "WAIT".

Data Pasar Real-Time:
- Tren H4/H1: {market_data.get('bias', 'NEUTRAL')} (kekuatan {market_data.get('strength', 0)})
- ADX H4: {market_data.get('adx', 0)}
- RSI H4: {market_data.get('rsi', 0)}
- Setup M15: {market_data.get('m15_signal', 'WAIT')}
- Alasan setup: {market_data.get('m15_reason', '')}
- Pola candlestick: {market_data.get('patterns', '')}

Aturan Penilaian:
1. Hanya berikan sinyal BUY atau SELL jika tren besar (H4/H1), setup M15, indikator pendukung (ADX/RSI), dan pola candlestick benar-benar selaras dan kuat.
2. Berikan confidence (0-100) secara realistis. Confidence >= 75 hanya diberikan jika kondisi pasar sangat valid tanpa keraguan.
3. Utamakan keselamatan modal. Lebih baik ketinggalan momentum daripada memaksakan sinyal palsu.

Jawab HANYA dalam format JSON murni tanpa teks tambahan di luar format:
{{"action": "BUY/SELL/WAIT", "confidence": 0-100, "reason": "jelaskan alasan teknikal secara akurat dan singkat"}}
"""

    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": "Anda adalah asisten trading profesional yang sangat disiplin dan wajib menghindari sinyal palsu atau halusinasi."},
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
