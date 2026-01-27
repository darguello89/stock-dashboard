from fastapi import FastAPI
from app.services.data_provider import get_latest_market_snapshot

app = FastAPI(title="Stock Dashboard API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/latest")
def latest(symbol: str = "AAPL"):
    return get_latest_market_snapshot(symbol)

