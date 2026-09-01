import pandas as pd

def detect_patterns(df: pd.DataFrame) -> dict:
    """
    Deteksi pola candlestick umum pada timeframe M15.
    Mengembalikan dict dengan boolean untuk setiap pola.
    """
    if len(df) < 3:
        return {}

    last = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]

    patterns = {}

    # Bullish Engulfing
    patterns['bullish_engulfing'] = (
        last['close'] > last['open'] and
        prev['close'] < prev['open'] and
        last['close'] > prev['open'] and
        last['open'] < prev['close']
    )

    # Bearish Engulfing
    patterns['bearish_engulfing'] = (
        last['close'] < last['open'] and
        prev['close'] > prev['open'] and
        last['close'] < prev['open'] and
        last['open'] > prev['close']
    )

    # Pin Bar Bullish (lower shadow panjang, upper kecil)
    body = abs(last['close'] - last['open'])
    lower_shadow = last['open'] - last['low'] if last['close'] > last['open'] else last['close'] - last['low']
    upper_shadow = last['high'] - last['close'] if last['close'] > last['open'] else last['high'] - last['open']
    patterns['bullish_pinbar'] = (
        lower_shadow > 2 * body and
        upper_shadow < body
    )

    # Pin Bar Bearish
    patterns['bearish_pinbar'] = (
        upper_shadow > 2 * body and
        lower_shadow < body
    )

    # Inside Bar
    patterns['inside_bar'] = (
        last['high'] < prev['high'] and
        last['low'] > prev['low']
    )

    # Doji
    patterns['doji'] = abs(last['close'] - last['open']) < 0.1 * (last['high'] - last['low'])

    return patterns
