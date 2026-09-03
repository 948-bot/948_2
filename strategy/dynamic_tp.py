import pandas as pd

def calculate_dynamic_tp(action: str, entry: float, df: pd.DataFrame) -> dict:
    if df.empty or 'atr' not in df.columns or len(df) < 14:
        return {"tp": None, "sl": None, "pips": None}

    atr = df['atr'].iloc[-1]
    if atr <= 0:
        return {"tp": None, "sl": None, "pips": None}

    # Hitung jarak TP berdasarkan ATR, tapi dikunci minimal 500 pips (5.0 dalam nilai harga emas)
    min_tp_pips = 500.0
    atr_tp_distance = 2.0 * atr
    
    # Ambil nilai yang paling besar antara ATR atau minimal 500 pips
    tp_distance = max(atr_tp_distance, min_tp_pips * 0.01)
    
    # Stop Loss diatur setengah dari jarak TP (Risk:Reward Ratio 1:2)
    sl_distance = tp_distance * 0.5

    if action == "BUY":
        sl = entry - sl_distance
        tp = entry + tp_distance
    elif action == "SELL":
        sl = entry + sl_distance
        tp = entry - tp_distance
    else:
        return {"tp": None, "sl": None, "pips": None}

    pips = tp_distance / 0.01

    return {
        "tp": round(tp, 2),
        "sl": round(sl, 2),
        "pips": round(pips, 0),
        "atr": round(atr, 2)
    }
