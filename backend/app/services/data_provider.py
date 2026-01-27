import time
from random import uniform

def get_latest_market_snapshot(symbol: str = "AAPL"):
    return {
        "symbol": symbol,
        "price": round(uniform(170, 190), 2),
        "timestamp": int(time.time())
    }

