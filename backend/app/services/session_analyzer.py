"""
Market Session Analyzer
Provides session-specific trading strategies and alerts based on market hours
"""
from typing import Dict, List
from datetime import datetime
import pytz

# Market hours in Eastern Time
MARKET_SESSIONS = {
    "premarket": {
        "start": "08:00",
        "end": "09:25",
        "strategy": "Scan for gappers, news, premarket levels",
        "focus": ["Gap analysis", "News impact", "Premarket momentum"],
        "max_position_size": 0.5,
        "risk_per_trade": 0.02,
        "key_levels": "Premarket high/low, previous close",
    },
    "opening": {
        "start": "09:30",
        "end": "10:00",
        "strategy": "Play ORB, don't chase",
        "focus": ["Opening Range Breakout", "Volume analysis", "First 30 min move"],
        "max_position_size": 1.0,
        "risk_per_trade": 0.025,
        "key_levels": "ORB levels (opening high/low +30 min)",
    },
    "morning": {
        "start": "10:00",
        "end": "12:00",
        "strategy": "VWAP plays, trend continuation",
        "focus": ["VWAP bounces", "Trend confirmation", "MA crossovers"],
        "max_position_size": 1.0,
        "risk_per_trade": 0.03,
        "key_levels": "VWAP, 20/50 EMA",
    },
    "lunch": {
        "start": "12:00",
        "end": "13:00",
        "strategy": "Reduce size, wider stops",
        "focus": ["Low volume", "Consolidation patterns", "News flow"],
        "max_position_size": 0.5,
        "risk_per_trade": 0.04,
        "key_levels": "Support/Resistance from morning",
    },
    "afternoon": {
        "start": "13:00",
        "end": "15:30",
        "strategy": "Mean reversion, breakout retests",
        "focus": ["Bounce trades", "Level retests", "Fed/News impact"],
        "max_position_size": 1.0,
        "risk_per_trade": 0.03,
        "key_levels": "Daily pivots, morning high/low",
    },
    "closing": {
        "start": "15:30",
        "end": "16:00",
        "strategy": "Don't hold overnight unless swing setup",
        "focus": ["Exit management", "Overnight gap risk", "Position squaring"],
        "max_position_size": 0.3,
        "risk_per_trade": 0.02,
        "key_levels": "Daily high/low, critical support/resistance",
    },
    "afterhours": {
        "start": "16:00",
        "end": "20:00",
        "strategy": "Monitor news, prepare for next day",
        "focus": ["Earnings reports", "News digestion", "Premarket prep"],
        "max_position_size": 0.0,
        "risk_per_trade": 0.0,
        "key_levels": "Level changes, news impact",
    }
}


def get_current_session() -> Dict:
    """
    Get current market session information
    Returns session details or None if market is closed
    """
    # Use Eastern Time
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    current_time = now.strftime("%H:%M")
    
    # Check if it's a weekday (0-4)
    weekday = now.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return {
            "session": "market_closed",
            "status": "weekend",
            "strategy": "Prepare for next week",
            "message": "Market closed - Weekend preparation"
        }
    
    # Check each session
    for session_name, session_info in MARKET_SESSIONS.items():
        session_start = session_info["start"]
        session_end = session_info["end"]
        
        if session_start <= current_time <= session_end:
            return {
                "session": session_name,
                "status": "active",
                "current_time": current_time,
                "start_time": session_start,
                "end_time": session_end,
                **session_info
            }
    
    # If outside trading hours
    if current_time < "08:00":
        return {
            "session": "before_premarket",
            "status": "waiting",
            "message": "Waiting for premarket session"
        }
    elif current_time > "20:00":
        return {
            "session": "after_hours",
            "status": "closed",
            "message": "Market closed - After hours session ended"
        }
    else:
        return {
            "session": "market_closed",
            "status": "closed",
            "message": "Market session not active"
        }


def calculate_gap_analysis(current_price: float, previous_close: float) -> Dict:
    """
    Calculate gap percentage and direction
    Used for pre-market analysis
    """
    if previous_close <= 0:
        return {"gap_percent": 0, "gap_direction": "neutral", "gap_size": 0}
    
    gap_percent = ((current_price - previous_close) / previous_close) * 100
    
    if gap_percent > 1:
        gap_direction = "up"
    elif gap_percent < -1:
        gap_direction = "down"
    else:
        gap_direction = "neutral"
    
    return {
        "gap_percent": round(gap_percent, 2),
        "gap_direction": gap_direction,
        "gap_size": "large" if abs(gap_percent) > 2 else "normal" if abs(gap_percent) > 1 else "small",
        "current_price": current_price,
        "previous_close": previous_close
    }


def calculate_orb(prices: List[float], volumes: List[float]) -> Dict:
    """
    Calculate Opening Range Breakout (ORB) levels
    First 30 minutes high and low create the ORB range
    """
    if len(prices) < 6:  # Need at least 6 data points for 30 min
        return {"orb_high": None, "orb_low": None, "orb_range": None}
    
    # Take first 6 candles (30 minutes at 5-min intervals)
    opening_prices = prices[:6]
    
    orb_high = max(opening_prices)
    orb_low = min(opening_prices)
    orb_range = orb_high - orb_low
    
    return {
        "orb_high": round(orb_high, 2),
        "orb_low": round(orb_low, 2),
        "orb_range": round(orb_range, 2),
        "current_price": round(prices[-1], 2),
        "above_orb": prices[-1] > orb_high,
        "below_orb": prices[-1] < orb_low
    }


def get_session_alerts(
    current_price: float,
    vwap_price: float,
    order_flow_ratio: float,
    volatility: float,
    session_info: Dict
) -> List[Dict]:
    """
    Generate session-specific trading alerts
    """
    alerts = []
    session_name = session_info.get("session", "")
    
    # Pre-market alerts
    if session_name == "premarket":
        if abs(order_flow_ratio - 1.0) > 0.5:
            alerts.append({
                "type": "info",
                "message": "Strong order flow imbalance detected in premarket",
                "action": "Prepare for gap move at market open"
            })
        if volatility > 10:
            alerts.append({
                "type": "warning",
                "message": "High premarket volatility",
                "action": "Be ready for large opening move"
            })
    
    # Opening alerts
    elif session_name == "opening":
        if abs(current_price - vwap_price) > vwap_price * 0.02:
            alerts.append({
                "type": "trade",
                "message": "Price significantly away from VWAP",
                "action": "Potential ORB play"
            })
    
    # Morning alerts
    elif session_name == "morning":
        if abs(current_price - vwap_price) < vwap_price * 0.01:
            alerts.append({
                "type": "trade",
                "message": "Price near VWAP level",
                "action": "Consider VWAP bounce play"
            })
    
    # Lunch alerts
    elif session_name == "lunch":
        if volatility < 2:
            alerts.append({
                "type": "info",
                "message": "Low volatility period - consolidation likely",
                "action": "Reduce position size, widen stops"
            })
    
    # Afternoon alerts
    elif session_name == "afternoon":
        if order_flow_ratio < 0.5:
            alerts.append({
                "type": "trade",
                "message": "Strong sell pressure - possible mean reversion",
                "action": "Watch for bounce setup"
            })
        elif order_flow_ratio > 1.5:
            alerts.append({
                "type": "trade",
                "message": "Strong buy pressure - trend continuation",
                "action": "Follow momentum"
            })
    
    # Closing alerts
    elif session_name == "closing":
        alerts.append({
            "type": "warning",
            "message": f"Closing session active - {session_info.get('strategy', '')}",
            "action": "Review positions, consider exits before 4 PM"
        })
    
    return alerts


def get_session_metrics(
    prices: List[float],
    volumes: List[float],
    current_price: float,
    previous_close: float,
    vwap_price: float,
    order_flow_ratio: float
) -> Dict:
    """
    Compile all session-specific metrics and guidance
    """
    session_info = get_current_session()
    session_name = session_info.get("session", "")
    
    metrics = {
        "session": session_info,
        "gap_analysis": calculate_gap_analysis(current_price, previous_close),
        "orb_levels": calculate_orb(prices, volumes),
        "alerts": [],
        "guidance": ""
    }
    
    # Calculate volatility for alerts
    volatility = 0
    if len(prices) > 1:
        returns = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]
        if returns:
            volatility = (sum((r - sum(returns) / len(returns)) ** 2 for r in returns) / len(returns)) ** 0.5
    
    # Get alerts
    metrics["alerts"] = get_session_alerts(
        current_price,
        vwap_price,
        order_flow_ratio,
        volatility,
        session_info
    )
    
    # Add session-specific guidance
    if session_name == "premarket":
        metrics["guidance"] = "Focus on gap levels and premarket movers. Check news for market-moving events."
    elif session_name == "opening":
        metrics["guidance"] = "Play the ORB but don't chase. Tight stops on range breakouts."
    elif session_name == "morning":
        metrics["guidance"] = "VWAP bounces and trend continuation trades are best. Confirm with volume."
    elif session_name == "lunch":
        metrics["guidance"] = "Reduce size due to low volume. Watch for news events. Wider stops recommended."
    elif session_name == "afternoon":
        metrics["guidance"] = "Mean reversion trades and level retests work best. Watch for Fed/economic data."
    elif session_name == "closing":
        metrics["guidance"] = "Focus on position management. Don't hold overnight unless strong swing setup."
    
    return metrics
