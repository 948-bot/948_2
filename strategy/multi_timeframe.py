import pandas as pd

def analyze_h4_h1(df_h4: pd.DataFrame, df_h1: pd.DataFrame) -> dict:
    """
    Analisis tren besar berdasarkan H4 dan H1.
    Menggabungkan EMA, MACD, ADX, Ichimoku.
    """
    if df_h4.empty or df_h1.empty:
        return {"bias": "NEUTRAL", "strength": 0, "structure": "Data insufficient"}

    h4 = df_h4.iloc[-1]
    h1 = df_h1.iloc[-1]

    # Kondisi H4
    h4_bull = (h4['ema20'] > h4['ema50'] > h4['ema100']) and h4['macd'] > h4['macd_signal'] and h4['adx'] > 20
    h4_bear = (h4['ema20'] < h4['ema50'] < h4['ema100']) and h4['macd'] < h4['macd_signal'] and h4['adx'] > 20

    # Kondisi H1
    h1_bull = (h1['ema20'] > h1['ema50']) and h1['macd_hist'] > 0 and h1['close'] > h1['senkou_span_a']
    h1_bear = (h1['ema20'] < h1['ema50']) and h1['macd_hist'] < 0 and h1['close'] < h1['senkou_span_a']

    # Gabungkan
    if h4_bull and h1_bull:
        bias = "BULLISH"
        strength = 90
        structure = "Tren naik kuat di H4 & H1"
    elif h4_bear and h1_bear:
        bias = "BEARISH"
        strength = 90
        structure = "Tren turun kuat di H4 & H1"
    elif h4_bull and not h1_bear:
        bias = "BULLISH"
        strength = 70
        structure = "H4 bullish, H1 netral/naik"
    elif h4_bear and not h1_bull:
        bias = "BEARISH"
        strength = 70
        structure = "H4 bearish, H1 netral/turun"
    else:
        bias = "NEUTRAL"
        strength = 30
        structure = "Tidak ada keselarasan tren"

    return {
        "bias": bias,
        "strength": strength,
        "structure": structure,
        "adx": h4['adx'],
        "rsi": h4['rsi']
    }
