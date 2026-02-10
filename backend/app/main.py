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
from app.services.advanced_indicators import combined_signal
from app.services.news_generator import generate_news
from app.services.session_analyzer import get_session_metrics

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
    # List of stocks to track (matches frontend)
    STOCK_SYMBOLS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'XOM', 'JNJ', 'JPM',
        'V', 'WMT', 'PG', 'UNH', 'BAC', 'MA', 'DIS', 'VZ', 'CSCO', 'INTC',
        'AMD', 'CRM', 'ADBE', 'IBM', 'TXN', 'QCOM', 'HON', 'LOW', 'CAT', 'GE',
        'BA', 'NFLX', 'PYPL', 'SPGI', 'SQ', 'UBER', 'LYFT', 'SNAP', 'PINS', 'ZM',
        'DOCU', 'TWLO', 'OKTA', 'WORKDAY', 'SLACK', 'MSTR', 'ROKU', 'TTWO', 'RBLX', 'SHOP',
        'CCI', 'ATVI', 'TMUS', 'DISH', 'CHTR', 'CMCSA', 'ROST', 'BJ', 'AZO', 'RH',
        'ETSY', 'DASH', 'O', 'STWD', 'MAR', 'HLT', 'OKE', 'CPRT', 'PLD', 'DRE',
        'PSA', 'EQR', 'AVB', 'ESS', 'ELS', 'EQC', 'ARE', 'SRC', 'RLJ', 'GDRX',
        'VICI', 'MGM', 'PEN', 'LPX', 'IRM', 'GPRE', 'AMT', 'EQIX', 'CORe', 'LAUR',
        'NRG', 'NEE', 'DUK', 'SO', 'AEP', 'XEL', 'SLG', 'DEI', 'SBAC', 'FSV'
    ]
    
    async def updater():
        while True:
            for symbol in STOCK_SYMBOLS:
                update_market_snapshot(symbol)
            await asyncio.sleep(5)

    asyncio.create_task(updater())

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/news")
def get_news():
    """Get dynamically generated market news"""
    return {"news": generate_news(count=8)}

@app.get("/session")
def get_session():
    """Get current market session and execution checklist"""
    # Get a stock for metrics calculation
    snapshot, prices = get_cached_snapshot("AAPL")
    current_price = snapshot.get("price", 100)
    previous_close = snapshot.get("previous_close", 100)
    
    # Generate volumes
    volumes = []
    import random
    for price in prices:
        base_volume = 5000000
        volume = base_volume * random.uniform(0.8, 1.5)
        volumes.append(volume)
    
    # Get signal for VWAP and order flow
    signal_analysis = combined_signal(prices, volumes, current_price)
    components = signal_analysis.get("components", {})
    vwap_price = components.get("vwap_price", current_price)
    order_flow = components.get("order_flow", {})
    order_flow_ratio = order_flow.get("ratio", 1.0)
    
    # Get session metrics
    session_metrics = get_session_metrics(
        prices,
        volumes,
        current_price,
        previous_close,
        vwap_price,
        order_flow_ratio
    )
    
    return session_metrics

@app.get("/latest")
def latest(symbol: str = "AAPL"):
    snapshot, prices = get_cached_snapshot(symbol)

    # Get current price and volumes from cached data
    current_price = snapshot.get("price", 100)
    
    # Generate volumes based on price history
    volumes = []
    for price in prices:
        # Simulate volume with some variation
        base_volume = 5000000  # 5M share average
        import random
        volume = base_volume * random.uniform(0.8, 1.5)
        volumes.append(volume)
    
    # Use advanced institutional algorithms
    signal_analysis = combined_signal(prices, volumes, current_price)

    return {
        "snapshot": snapshot,
        "signal_analysis": signal_analysis,
        "algorithms_used": [
            "MARKET OPEN SETUP",
            "ORDER FLOW",
            "VWAP POSITIONING",
            "MICROSTRUCTURE",
            "VOLUME PROFILE"
        ]
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
