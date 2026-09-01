def validate_risk(signal_payload: dict, action: str) -> tuple:
    tp = signal_payload.get("tp")
    sl = signal_payload.get("sl")
    entry = signal_payload.get("entry")
    atr = signal_payload.get("atr", 0)

    if tp is None or sl is None or entry is None:
        return False, "TP/SL/Entry tidak lengkap"

    sl_distance = abs(entry - sl)
    tp_distance = abs(tp - entry)

    if sl_distance <= 0 or tp_distance <= 0:
        return False, "Jarak SL/TP tidak valid"

    if tp_distance < sl_distance:
        return False, f"Risk/Reward < 1:1 (TP={tp_distance:.2f}, SL={sl_distance:.2f})"

    min_sl_pips = 100 * 0.01
    if sl_distance < min_sl_pips:
        return False, f"SL terlalu dekat (< {min_sl_pips})"

    if atr < 2.5:
        return False, f"Volatilitas terlalu rendah (ATR={atr:.2f})"

    return True, "OK"
