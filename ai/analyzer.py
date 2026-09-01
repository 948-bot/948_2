def calculate_signal_score(m30_context: dict, m15_setup: dict, higher_tf: dict) -> dict:
    """
    Hitung skor 0-100 berdasarkan sinyal dan konfirmasi.
    """
    signal = m15_setup.get("signal", "WAIT")
    if signal == "WAIT":
        return {"action": "WAIT", "score": 0}

    bias = higher_tf.get("bias", "NEUTRAL")
    strength = higher_tf.get("strength", 0)
    score = 0

    # Skor dasar arah selaras dengan tren besar
    if bias == "BULLISH" and signal == "BUY":
        score += 50
    elif bias == "BEARISH" and signal == "SELL":
        score += 50
    else:
        return {"action": "WAIT", "score": 0}  # tidak selaras, langsung tolak

    # Skor dari kekuatan tren (0-100 -> tambah maks 30)
    score += int(strength * 0.3)

    # Skor dari ADX
    adx = higher_tf.get("adx", 0)
    if adx > 30:
        score += 10
    elif adx > 25:
        score += 5

    # Skor dari RSI (tidak ekstrem)
    rsi = m30_context.get("rsi", 50)
    if 45 <= rsi <= 65:
        score += 10
    elif 40 <= rsi <= 70:
        score += 5

    # Skor tambahan jika alasan mengandung "lengkap"
    if "lengkap" in m15_setup.get("reason", ""):
        score += 10

    score = min(score, 100)

    # Hanya eksekusi jika skor >= 80
    if score >= 80:
        action = signal
    else:
        action = "WAIT"

    return {"action": action, "score": score}
