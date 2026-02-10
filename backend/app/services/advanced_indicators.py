import time
from typing import List, Dict, Tuple

def vwap(prices: List[float], volumes: List[float]) -> float | None:
    """
    Volume Weighted Average Price (VWAP)
    Cumulative TP*V / Cumulative V
    Indicates fair value and support/resistance
    """
    if len(prices) < 2 or len(volumes) < 2:
        return None
    
    tp_volume = sum(p * v for p, v in zip(prices, volumes))
    total_volume = sum(volumes)
    
    if total_volume == 0:
        return None
    
    return round(tp_volume / total_volume, 2)

def order_flow(prices: List[float], volumes: List[float]) -> Dict:
    """
    Order Flow Analysis
    Measures buy vs sell pressure based on price action and volume
    """
    if len(prices) < 2 or len(volumes) < 2:
        return {"buy_pressure": 0.5, "sell_pressure": 0.5, "ratio": 1.0}
    
    buy_volume = 0
    sell_volume = 0
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            # Up move = buy volume
            buy_volume += volumes[i]
        elif prices[i] < prices[i-1]:
            # Down move = sell volume
            sell_volume += volumes[i]
        else:
            # No change, split evenly
            buy_volume += volumes[i] * 0.5
            sell_volume += volumes[i] * 0.5
    
    total_volume = buy_volume + sell_volume
    if total_volume == 0:
        return {"buy_pressure": 0.5, "sell_pressure": 0.5, "ratio": 1.0}
    
    buy_pressure = round(buy_volume / total_volume, 2)
    sell_pressure = round(sell_volume / total_volume, 2)
    ratio = round(buy_volume / (sell_volume + 0.001), 2)
    
    return {
        "buy_pressure": buy_pressure,
        "sell_pressure": sell_pressure,
        "ratio": ratio  # >1 = more buy volume, <1 = more sell volume
    }

def volume_profile(prices: List[float], volumes: List[float], bins: int = 10) -> Dict:
    """
    Volume Profile
    Identifies price levels with high trading activity
    Used for support/resistance and liquidity analysis
    """
    if len(prices) < 2 or len(volumes) < 2:
        return {"poc": prices[-1] if prices else 0, "value_area": []}
    
    min_price = min(prices)
    max_price = max(prices)
    
    if min_price == max_price:
        return {"poc": min_price, "value_area": [min_price]}
    
    # Create price bins
    bin_size = (max_price - min_price) / bins
    bin_volumes = {}
    
    for price, volume in zip(prices, volumes):
        bin_key = round((price - min_price) / bin_size * 2) / 2 + min_price
        bin_volumes[bin_key] = bin_volumes.get(bin_key, 0) + volume
    
    # Find Point of Control (highest volume price level)
    poc = max(bin_volumes, key=bin_volumes.get)
    
    # Find Value Area (70% of volume)
    total_vol = sum(bin_volumes.values())
    target_vol = total_vol * 0.7
    
    sorted_bins = sorted(bin_volumes.items(), key=lambda x: x[1], reverse=True)
    value_area = []
    cumulative_vol = 0
    
    for price_level, vol in sorted_bins:
        value_area.append(round(price_level, 2))
        cumulative_vol += vol
        if cumulative_vol >= target_vol:
            break
    
    return {
        "poc": round(poc, 2),  # Point of Control
        "value_area": sorted(value_area)
    }

def microstructure(prices: List[float], volumes: List[float]) -> Dict:
    """
    Market Microstructure Analysis
    Bid-Ask dynamics, spreads, and order imbalance
    """
    if len(prices) < 2 or len(volumes) < 2:
        return {"volatility": 0, "imbalance": 0.5, "efficiency": 0.5}
    
    # Calculate volatility (standard deviation of returns)
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] != 0 else 0
        returns.append(ret)
    
    if returns:
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = round((variance ** 0.5) * 100, 2)
    else:
        volatility = 0
    
    # Order imbalance (volume-weighted price change)
    recent_prices = prices[-20:] if len(prices) >= 20 else prices
    recent_volumes = volumes[-20:] if len(volumes) >= 20 else volumes
    
    if recent_prices:
        price_range = max(recent_prices) - min(recent_prices)
        current_position = (recent_prices[-1] - min(recent_prices)) / (price_range + 0.001)
        imbalance = round(current_position, 2)
    else:
        imbalance = 0.5
    
    # Market efficiency (how price moves relative to volume)
    if recent_volumes:
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        price_move = abs(recent_prices[-1] - recent_prices[0])
        efficiency = round(min(price_move / (avg_volume + 0.001), 1.0), 2)
    else:
        efficiency = 0.5
    
    return {
        "volatility": volatility,
        "imbalance": imbalance,  # 0=at low, 1=at high, 0.5=middle
        "efficiency": efficiency
    }

def market_open_setup(prices: List[float], volumes: List[float]) -> Dict:
    """
    Market Open Setup
    Identifies opening conditions and morning momentum
    """
    if len(prices) < 5 or len(volumes) < 5:
        return {"gap": 0, "momentum": 0.5, "strength": 0}
    
    open_price = prices[0]
    prev_close = prices[0] if len(prices) > 0 else prices[-1]
    current_price = prices[-1]
    current_volume = volumes[-1]
    avg_volume = sum(volumes) / len(volumes)
    
    # Gap calculation
    gap = round(((current_price - open_price) / open_price * 100), 2) if open_price != 0 else 0
    
    # Morning momentum (first 5 candles)
    early_prices = prices[:min(5, len(prices))]
    if early_prices:
        momentum = (early_prices[-1] - early_prices[0]) / early_prices[0] * 100 if early_prices[0] != 0 else 0
    else:
        momentum = 0
    
    # Volume strength compared to average
    volume_strength = round(current_volume / (avg_volume + 0.001), 2)
    
    # Setup strength (0-100)
    strength_score = 0
    if abs(gap) > 1:  # Significant gap
        strength_score += 20
    if abs(momentum) > 1:  # Momentum present
        strength_score += 20
    if volume_strength > 1.5:  # High volume
        strength_score += 20
    if gap > 0 and momentum > 0:  # Gap and momentum aligned
        strength_score += 40
    
    return {
        "gap": gap,
        "momentum": round(momentum, 2),
        "volume_strength": round(volume_strength, 2),
        "setup_strength": min(strength_score, 100)
    }

def combined_signal(
    prices: List[float],
    volumes: List[float],
    current_price: float
) -> Dict:
    """
    Combined Real-Time Signal
    SIGNAL = MARKET_OPEN_SETUP × ORDER_FLOW × VWAP_POSITIONING × MICROSTRUCTURE × VOLUME_PROFILE
    """
    
    # Ensure we have valid data
    if not prices or not volumes or len(prices) < 2 or len(volumes) < 2:
        return {
            "signal": "HOLD",
            "confidence": 0.5,
            "combined_score": 0.5,
            "components": {
                "market_open_setup": {"gap": 0, "momentum": 0, "setup_strength": 0},
                "order_flow": {"buy_pressure": 0.5, "sell_pressure": 0.5, "ratio": 1},
                "vwap_price": current_price,
                "vwap_distance": 0,
                "microstructure": {"volatility": 0, "imbalance": 0.5, "efficiency": 0.5},
                "volume_profile": {"poc": current_price, "value_area": [current_price]}
            }
        }
    
    # Get all components
    setup = market_open_setup(prices, volumes)
    flow = order_flow(prices, volumes)
    vwap_price = vwap(prices, volumes)
    micro = microstructure(prices, volumes)
    vol_profile = volume_profile(prices, volumes)
    
    # VWAP positioning (how far from VWAP)
    if vwap_price:
        vwap_distance = ((current_price - vwap_price) / vwap_price) * 100
        above_vwap = 1.0 if current_price > vwap_price else 0.0
    else:
        vwap_distance = 0
        above_vwap = 0.5
    
    # Normalize all signals to 0-1 range
    setup_score = setup.get("setup_strength", 0) / 100
    flow_score = flow.get("buy_pressure", 0.5)
    vwap_score = max(0, min(1, 0.5 + (above_vwap - 0.5) * 2))
    micro_score = micro.get("efficiency", 0.5)
    vol_score = max(0, min(1, 0.5 + micro.get("imbalance", 0.5)))
    
    # Combined weighted signal
    weights = {
        "setup": 0.2,
        "flow": 0.25,
        "vwap": 0.2,
        "micro": 0.15,
        "volume": 0.2
    }
    
    combined = (
        setup_score * weights["setup"] +
        flow_score * weights["flow"] +
        vwap_score * weights["vwap"] +
        micro_score * weights["micro"] +
        vol_score * weights["volume"]
    )
    
    # Generate signal based on combined score
    if combined > 0.75:
        signal = "STRONG BUY"
        confidence = combined
    elif combined > 0.60:
        signal = "BUY"
        confidence = combined
    elif combined > 0.40:
        signal = "HOLD"
        confidence = 0.5
    elif combined > 0.25:
        signal = "SELL"
        confidence = 1 - combined
    else:
        signal = "STRONG SELL"
        confidence = 1 - combined
    
    return {
        "signal": signal,
        "confidence": round(confidence, 2),
        "combined_score": round(combined, 2),
        "components": {
            "market_open_setup": setup,
            "order_flow": flow,
            "vwap_price": vwap_price,
            "vwap_distance": round(vwap_distance, 2) if vwap_price else 0,
            "microstructure": micro,
            "volume_profile": vol_profile
        }
    }
