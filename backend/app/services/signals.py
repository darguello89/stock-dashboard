def generate_signal(rsi_value: float | None):
    if rsi_value is None:
        return {"signal": "WAIT", "confidence": 0.0}

    if rsi_value < 30:
        return {"signal": "BUY", "confidence": round((30 - rsi_value) / 30, 2)}
    if rsi_value > 70:
        return {"signal": "SELL", "confidence": round((rsi_value - 70) / 30, 2)}

    return {"signal": "HOLD", "confidence": 0.5}

