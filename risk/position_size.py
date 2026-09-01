def calculate_position_size(balance: float, entry: float, sl: float, risk_percent: float = 2.0) -> dict:
    risk_amount = balance * (risk_percent / 100)
    sl_distance = abs(entry - sl)

    if sl_distance == 0:
        return {"lot": 0.0, "risk_amount": 0.0, "risk_percent": risk_percent}

    lot = risk_amount / (sl_distance * 100)
    lot = max(0.01, round(lot, 2))

    return {
        "lot": lot,
        "risk_amount": round(risk_amount, 2),
        "risk_percent": risk_percent
    }
