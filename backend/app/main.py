from fastapi import FastAPI
import asyncio

from app.services.data_provider import (
    update_market_snapshot,
    get_cached_snapshot
)
from app.services.indicators import rsi, ema
from app.services.signals import generate_signal

app = FastAPI(title="Stock Dashboard API")

@app.on_event("startup")
async def start_background_tasks():
    async def updater():
        while True:
            update_market_snapshot("AAPL")
            update_market_snapshot("SPY")
            await asyncio.sleep(5)

    asyncio.create_task(updater())

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/latest")
def latest(symbol: str = "AAPL"):
    snapshot, prices = get_cached_snapshot(symbol)

    rsi_value = rsi(prices)
    ema_20 = ema(prices, 20)

    signal = generate_signal(rsi_value)

    return {
        "snapshot": snapshot,
        "indicators": {
            "rsi": rsi_value,
            "ema_20": ema_20
        },
        "signal": signal
    }

