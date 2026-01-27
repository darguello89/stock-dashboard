from typing import List

def ema(prices: List[float], period: int) -> float | None:
    if len(prices) < period:
        return None

    k = 2 / (period + 1)
    ema_value = prices[0]

    for price in prices[1:]:
        ema_value = price * k + ema_value * (1 - k)

    return round(ema_value, 2)

def rsi(prices: List[float], period: int = 14) -> float | None:
    if len(prices) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, period + 1):
        delta = prices[-i] - prices[-i - 1]
        if delta > 0:
            gains.append(delta)
        else:
            losses.append(abs(delta))

    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

