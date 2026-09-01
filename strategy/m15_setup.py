import pandas as pd

def evaluate_m15_setup(df: pd.DataFrame, m30_context: dict, patterns: dict) -> dict:
    """
    Evaluasi setup M15 dengan multi-konfirmasi dan pola candlestick.
    """
    if df.empty or len(df) < 30:
        return {"signal": "WAIT", "reason": "Data insufficient"}

    last = df.iloc[-1]
    prev = df.iloc[-2]
    bias = m30_context.get("bias", "NEUTRAL")

    # Kondisi umum
    rsi_ok_buy = 45 < last['rsi'] < 65
    rsi_ok_sell = 35 < last['rsi'] < 55

    macd_hist_rising = last['macd_hist'] > prev['macd_hist']
    macd_hist_falling = last['macd_hist'] < prev['macd_hist']

    stoch_cross_up = last['stoch_k'] > last['stoch_d'] and prev['stoch_k'] <= prev['stoch_d']
    stoch_cross_down = last['stoch_k'] < last['stoch_d'] and prev['stoch_k'] >= prev['stoch_d']

    near_bb_lower = last['close'] <= last['bb_lower'] * 1.01
    near_bb_upper = last['close'] >= last['bb_upper'] * 0.99

    # Pola candlestick
    bullish_pattern = patterns.get('bullish_engulfing', False) or patterns.get('bullish_pinbar', False)
    bearish_pattern = patterns.get('bearish_engulfing', False) or patterns.get('bearish_pinbar', False)

    # Sinyal BUY
    if bias == "BULLISH":
        buy_conditions = [
            rsi_ok_buy,
            macd_hist_rising,
            stoch_cross_up or near_bb_lower,
            bullish_pattern  # wajib ada pola bullish
        ]
        if all(buy_conditions):
            return {"signal": "BUY", "reason": "Konfirmasi bullish lengkap (pola + indikator)"}

    # Sinyal SELL
    elif bias == "BEARISH":
        sell_conditions = [
            rsi_ok_sell,
            macd_hist_falling,
            stoch_cross_down or near_bb_upper,
            bearish_pattern  # wajib ada pola bearish
        ]
        if all(sell_conditions):
            return {"signal": "SELL", "reason": "Konfirmasi bearish lengkap (pola + indikator)"}

    return {"signal": "WAIT", "reason": "Belum ada konfirmasi lengkap"}
