import random
import time

# News templates for different categories
NEWS_TEMPLATES = [
    {
        "category": "monetary_policy",
        "headlines": [
            "Fed Signals Possible Rate {action} in Coming Months",
            "Central Bank Maintains {stance} Stance on Interest Rates",
            "Federal Reserve Chair Hints at {direction} Monetary Policy",
            "Markets Rally as Fed Indicates {tone} Economic Outlook"
        ],
        "sources": ["Reuters", "Bloomberg", "CNBC"],
        "affected_stocks": [["AAPL", "MSFT", "GOOGL"], ["JPM", "BAC", "GS"], ["TSLA", "AMZN", "NVDA"]]
    },
    {
        "category": "tech",
        "headlines": [
            "{company} Announces {achievement} Breaking Industry Records",
            "{company} Reports {performance} Quarterly Earnings",
            "{company} Unveils New {product} Strategy",
            "AI Breakthrough: {company} Leads Innovation Race"
        ],
        "sources": ["TechCrunch", "The Verge", "Wired"],
        "companies": ["Apple", "Microsoft", "NVIDIA", "Meta", "Amazon", "Google"],
        "affected_stocks": [["AAPL", "MSFT", "NVDA"], ["META", "GOOGL", "AMZN"], ["TSLA", "CRM", "ADBE"]]
    },
    {
        "category": "energy",
        "headlines": [
            "Oil Prices {movement} as {event} Impacts Global Markets",
            "Energy Stocks {trend} Following {catalyst} Report",
            "Crude Oil Hits {milestone} Amid {situation}",
            "Renewable Energy Sector Shows {performance} Growth"
        ],
        "sources": ["Bloomberg Energy", "Reuters Energy", "Oil & Gas Journal"],
        "affected_stocks": [["XOM", "CVX", "NEE"], ["DUK", "SO", "AEP"], ["NRG", "XEL", "PSA"]]
    },
    {
        "category": "finance",
        "headlines": [
            "{bank} Reports {result} Q{quarter} Earnings",
            "Banking Sector {trend} on {factor} Performance",
            "{bank} Announces {action} to Boost Market Position",
            "Financial Services Stocks {movement} Following Fed Meeting"
        ],
        "sources": ["Financial Times", "WSJ", "Bloomberg Markets"],
        "banks": ["JPMorgan", "Bank of America", "Goldman Sachs", "Morgan Stanley"],
        "affected_stocks": [["JPM", "BAC", "GS"], ["V", "MA", "PYPL"], ["SPGI", "JPM", "WMT"]]
    },
    {
        "category": "retail",
        "headlines": [
            "{retailer} Beats Expectations with {metric} Sales Growth",
            "E-commerce Boom: {company} Captures Market Share",
            "Retail Sector {trend} as Consumer Spending {direction}",
            "{company} Expands Operations with {initiative}"
        ],
        "sources": ["Retail Dive", "Business Insider", "CNBC"],
        "retailers": ["Walmart", "Amazon", "Target", "Costco"],
        "affected_stocks": [["WMT", "AMZN", "ROST"], ["DIS", "DASH", "SHOP"], ["ETSY", "BJ", "AZO"]]
    }
]

WORD_VARIATIONS = {
    "action": ["Hold", "Cut", "Adjustment", "Increase"],
    "stance": ["Cautious", "Hawkish", "Dovish", "Balanced"],
    "direction": ["Accommodative", "Tightening", "Neutral", "Flexible"],
    "tone": ["Optimistic", "Cautious", "Positive", "Mixed"],
    "achievement": ["Record Revenue", "Major Breakthrough", "Strategic Partnership", "Product Launch"],
    "performance": ["Strong", "Mixed", "Better-Than-Expected", "Solid"],
    "product": "Innovation Technology Development AI".split(),
    "movement": ["Surge", "Climb", "Rally", "Rise"],
    "trend": ["Rally", "Gain Momentum", "Show Strength", "Outperform"],
    "event": ["OPEC Meeting", "Geopolitical Tensions", "Supply Chain Shifts", "Demand Surge"],
    "catalyst": ["Production", "Inventory", "Demand", "Supply"],
    "milestone": ["3-Month High", "6-Month High", "New Peak", "Record Level"],
    "situation": ["Market Dynamics", "Global Trade Shifts", "Economic Recovery", "Supply Concerns"],
    "result": ["Strong", "Record", "Better-than-Expected", "Impressive"],
    "quarter": ["1", "2", "3", "4"],
    "factor": ["Strong Earnings", "Market Confidence", "Economic Data", "Investor Sentiment"],
    "metric": ["Record", "15%", "Strong", "Double-Digit"],
    "initiative": ["New Store Openings", "Technology Investment", "Market Expansion", "Digital Transformation"]
}

def generate_sentiment():
    """Generate random sentiment for affected stocks"""
    sentiments = ["positive", "negative", "neutral"]
    return random.choice(sentiments)

def generate_news_item(template):
    """Generate a single news item from template"""
    headline = random.choice(template["headlines"])
    
    # Fill in template variables
    for key, values in WORD_VARIATIONS.items():
        if f"{{{key}}}" in headline:
            headline = headline.replace(f"{{{key}}}", random.choice(values))
    
    # Special handling for company/bank/retailer
    if "{company}" in headline:
        company = random.choice(template.get("companies", ["Tech Giant", "Major Corporation"]))
        headline = headline.replace("{company}", company)
    if "{bank}" in headline:
        bank = random.choice(template.get("banks", ["Major Bank"]))
        headline = headline.replace("{bank}", bank)
    if "{retailer}" in headline:
        retailer = random.choice(template.get("retailers", ["Major Retailer"]))
        headline = headline.replace("{retailer}", retailer)
    
    # Generate excerpt based on category
    excerpts = {
        "monetary_policy": "Federal Reserve officials indicate policy direction impacting tech and financial sectors, with markets responding to economic outlook statements.",
        "tech": "Technology sector shows strong performance with innovative product launches and strategic initiatives driving investor confidence.",
        "energy": "Energy markets respond to global supply dynamics and geopolitical developments affecting crude oil prices and renewable investments.",
        "finance": "Banking sector demonstrates robust quarterly performance with strong loan growth and investment banking revenue.",
        "retail": "Consumer spending patterns shift as major retailers adapt to e-commerce trends and changing shopping behaviors."
    }
    
    # Select affected stocks and assign sentiments
    stock_set = random.choice(template["affected_stocks"])
    affected_stocks = [
        {"symbol": stock, "sentiment": generate_sentiment()}
        for stock in stock_set
    ]
    
    # Generate timestamp (between 1 and 12 hours ago)
    hours_ago = random.randint(1, 12)
    
    return {
        "source": random.choice(template["sources"]),
        "headline": headline,
        "excerpt": excerpts.get(template["category"], "Market activity reflects evolving economic conditions."),
        "affected_stocks": affected_stocks,
        "timestamp": f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago",
        "category": template["category"]
    }

def generate_news(count=8):
    """Generate multiple news items"""
    news_items = []
    templates = random.sample(NEWS_TEMPLATES, min(count, len(NEWS_TEMPLATES)))
    
    for template in templates:
        news_items.append(generate_news_item(template))
    
    # Fill remaining slots if needed
    while len(news_items) < count:
        template = random.choice(NEWS_TEMPLATES)
        news_items.append(generate_news_item(template))
    
    return news_items
