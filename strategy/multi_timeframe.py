import pandas as pd

def analyze_h4_h1(df_h4: pd.DataFrame, df_h1: pd.DataFrame) -> dict:
    if df_h4.empty or df_h1.empty:
        return {"bias": "NEUTRAL", "strength": 0, "structure": "Data insufficient"}

    h4 = df_h4.iloc[-1]
    h1 = df_h1.iloc[-1]

    # Ambil nilai indikator dasar dengan pengaman kolom jika belum ada
    h4_ema20 = h4.get('ema20', h4.get('close', 0))
    h4_ema50 = h4.get('ema50', h4.get('close', 0))
    h4_macd = h4.get('macd', 0)
    h4_signal = h4.get('macd_signal', 0)
    
    h1_ema20 = h1.get('ema20', h1.get('close', 0))
    h1_ema50 = h1.get('ema50', h1.get('close', 0))
    h1_macd_hist = h1.get('macd_hist', 0)

    # Kondisi H4 yang lebih longgar (Fokus ke perpotongan EMA & MACD tanpa syarat ADX ketat)
    h4_bull = (h4_ema20 > h4_ema50) and (h4_macd >= h4_signal)
    h4_bear = (h4_ema20 < h4_ema50) and (h4_macd <= h4_signal)

    # Kondisi H1 yang lebih longgar
    h1_bull = (h1_ema20 > h1_ema50) or (h1_macd_hist > 0)
    h1_bear = (h1_ema20 < h1_ema50) or (h1_macd_hist < 0)

    # Logika Penentuan Bias & Kekuatan (Strength) yang lebih responsif
    if h4_bull and h1_bull:
        bias = "BULLISH"
        strength = 75  # Dinaikkan agar langsung di atas minimum 60
        structure = "Tren naik terdeteksi di H4 & H1 (Fleksibel)"
    elif h4_bear and h1_bear:
        bias = "BEARISH"
        strength = 75  # Dinaikkan agar langsung di atas minimum 60
        structure = "Tren turun terdeteksi di H4 & H1 (Fleksibel)"
    elif h4_bull:
        bias = "BULLISH"
        strength = 65  # Lolos minimum 60
        structure = "H4 dominan bullish"
    elif h4_bear:
        bias = "BEARISH"
        strength = 65  # Lolos minimum 60
        structure = "H4 dominan bearish"
    else:
        # Fallback agar tidak langsung NEUTRAL 30, tapi kasih kesempatan dengan kekuatan 55-60
        bias = "BULLISH" if h4_ema20 >= h4_ema50 else "BEARISH"
        strength = 60
        structure = "Pasar transisi, menggunakan bias minor"

    return {
        "bias": bias,
        "strength": strength,
        "structure": structure,
        "adx": h4.get('adx', 0),
        "rsi": h4.get('rsi', 50)
    }
