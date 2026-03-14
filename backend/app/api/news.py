from fastapi import APIRouter, HTTPException
import requests
from datetime import datetime, timedelta

router = APIRouter()

# Replace with your actual NewsAPI.org Key
NEWS_API_KEY = "bba115d4b359435199c2ba5dd54b9b24"
BASE_URL = "https://newsapi.org/v2/everything"

@router.get("/")
async def get_market_news(symbol: str = None):
    """
    Fetches the latest business news. If a symbol is provided, 
    it filters specifically for that company.
    """
    # Create a query: if symbol exists, search for it; otherwise, general Indian market
    query = f"{symbol} stock India" if symbol else "Indian Stock Market OR NSE OR Nifty"
    
    # Restrict news to the last 7 days for relevancy
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": NEWS_API_KEY,
        "pageSize": 10
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data.get("status") != "ok":
            raise HTTPException(status_code=500, detail=data.get("message", "News fetch failed"))

        articles = []
        for art in data.get("articles", []):
            articles.append({
                "title": art["title"],
                "source": art["source"]["name"],
                "published_at": art["publishedAt"],
                "url": art["url"],
                "description": art["description"] or "No description available.",
                "image": art.get("urlToImage") or "📈" # Fallback icon
            })
        
        return {"count": len(articles), "news": articles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))