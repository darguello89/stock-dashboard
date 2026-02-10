from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os

from app.services.data_provider import (
    update_market_snapshot,
    get_cached_snapshot
)
from app.services.indicators import rsi, ema
from app.services.signals import generate_signal

app = FastAPI(title="Stock Dashboard API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Serve static files and frontend
# Get absolute path to frontend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.abspath(os.path.join(current_dir, "../../frontend"))

@app.get("/")
async def serve_root():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return {"error": "Frontend not found"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    file_path = os.path.join(frontend_path, full_path)
    # Prevent directory traversal
    if os.path.abspath(file_path).startswith(frontend_path):
        if os.path.isfile(file_path):
            return FileResponse(file_path)
    # For SPA, serve index.html if file not found
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return {"error": "Frontend not found"}
