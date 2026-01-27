import time
from random import uniform
from app.services.cache import market_cache, price_history

MAX_HISTORY = 100

def update_market_snapshot(symbol: str = "AAPL"):
    price = round(uniform(170, 190), 2)

    price_history.setdefault(symbol, []).append(price)
    price_history[symbol] = price_history[symbol][-MAX_HISTORY:]

    market_cache[symbol] = {
        "symbol": symbol,
        "price": price,
        "timestamp": int(time.time())
    }

def get_cached_snapshot(symbol: str = "AAPL"):
    return market_cache.get(symbol), price_history.get(symbol, [])

