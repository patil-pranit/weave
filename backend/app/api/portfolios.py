from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import yfinance as yf
import pandas as pd
import pandas_ta_classic as ta

router = APIRouter()

class PortfolioRequest(BaseModel):
    investment_amount: float
    risk_appetite: int  # 1 (Cons) to 5 (Aggr)
    sectors: List[str]

# Pre-defined universe of top Indian stocks per sector
STOCK_UNIVERSE = {
    "IT": ["TCS", "INFY", "WIPRO", "HCLTECH"],
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK"],
    "Energy": ["RELIANCE", "ONGC", "BPCL"],
    "FMCG": ["ITC", "HUL", "NESTLEIND"]
}

def calculate_stock_score(symbol: str, risk_level: int):
    """Ranks a stock based on technicals and fundamentals."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        # Fetch 6 months of data for indicators
        df = ticker.history(period="6mo")
        if df.empty: return 0

        # 1. Technical: RSI (14)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        current_rsi = df['RSI'].iloc[-1]
        
        # Scoring RSI: 50-60 is ideal (Score: 40/40)
        rsi_score = 0
        if 45 <= current_rsi <= 65: rsi_score = 40
        elif current_rsi > 70: rsi_score = 10 # Overbought
        else: rsi_score = 25 # Oversold/Weak

        # 2. Fundamental: ROE (from ticker.info)
        info = ticker.info
        roe = info.get('returnOnEquity', 0)
        roe_score = min(roe * 100, 30) # Max 30 points

        # 3. Risk Match: Beta vs User Appetite
        beta = info.get('beta', 1.0)
        risk_score = 0
        # If user is conservative (1-2), prefer Beta < 1
        if risk_level <= 2 and beta < 1: risk_score = 30
        # If user is aggressive (4-5), prefer Beta > 1.1
        elif risk_level >= 4 and beta > 1.1: risk_score = 30
        else: risk_score = 15

        return round(rsi_score + roe_score + risk_score, 2)
    except:
        return 0

@router.post("/generate")
async def generate_portfolio(req: PortfolioRequest):
    results = []
    
    # Filter universe based on selected sectors
    target_symbols = []
    for sector in req.sectors:
        target_symbols.extend(STOCK_UNIVERSE.get(sector, []))

    if not target_symbols:
        raise HTTPException(status_code=400, detail="No stocks found for selected sectors.")

    # Score and rank each stock
    for sym in target_symbols:
        score = calculate_stock_score(sym, req.risk_appetite)
        ticker = yf.Ticker(f"{sym}.NS")
        price = ticker.fast_info.last_price

        results.append({
            "symbol": sym,
            "score": score,
            "price": round(price, 2),
            "name": ticker.info.get('longName', sym)
        })

    # Sort by score and take top 5
    top_stocks = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    
    # Simple Equal Allocation Logic
    allocation_per_stock = req.investment_amount / len(top_stocks)
    for stock in top_stocks:
        stock["allocation"] = round(allocation_per_stock, 2)
        stock["shares"] = int(allocation_per_stock / stock["price"])

    return {
        "strategy": "Growth/Momentum",
        "composite_score": sum(s['score'] for s in top_stocks) / len(top_stocks),
        "holdings": top_stocks
    }