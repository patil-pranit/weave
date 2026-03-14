# from fastapi import APIRouter, HTTPException
# from app.utils.data_fetcher import get_nse_stock_price

# router = APIRouter()

# @router.get("/{symbol}", response_model=float)
# def fetch_live_price(symbol: str):
#     try:
#         price = get_nse_stock_price(symbol)
#         return price
#     except Exception as e:
#         raise HTTPException(status_code=404, detail="Stock not found or NSE unavailable")

"""New code"""

from fastapi import APIRouter, HTTPException, Query
import yfinance as yf
from typing import List, Optional
import pandas as pd

router = APIRouter()

# Helper to format ticker for Indian markets (NSE/BSE)
def format_ticker(symbol: str):
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        return f"{symbol}.NS"  # Default to NSE
    return symbol

@router.get("/{symbol}/price")
async def get_stock_price(symbol: str):
    """
    Fetches the live price and today's change for a specific Indian stock.
    """
    try:
        ticker_sym = format_ticker(symbol)
        ticker = yf.Ticker(ticker_sym)
        data = ticker.fast_info
        
        return {
            "symbol": symbol,
            "ltp": round(data.last_price, 2),
            "currency": data.currency,
            "exchange": data.exchange,
            "timestamp": data.last_volume # Approximation for live status
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock data not found: {str(e)}")

@router.get("/{symbol}/history")
async def get_stock_history(
    symbol: str, 
    period: str = Query("1y", description="1d, 5d, 1mo, 6mo, 1y, 5y, max"),
    interval: str = Query("1d", description="1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """
    Provides historical price points for the Chart.js line charts.
    """
    try:
        ticker_sym = format_ticker(symbol)
        df = yf.download(ticker_sym, period=period, interval=interval)
        
        if df.empty:
            raise ValueError("No data found")

        # Formatting for Chart.js: Labels (Dates) and Data (Close Prices)
        history_data = {
            "labels": df.index.strftime('%Y-%m-%d').tolist(),
            "prices": df['Close'].round(2).tolist()
        }
        return history_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{symbol}/fundamentals")
async def get_stock_fundamentals(symbol: str):
    """
    Sourcing Balance Sheet, Results, and Company Info.
    """
    try:
        ticker_sym = format_ticker(symbol)
        ticker = yf.Ticker(ticker_sym)
        info = ticker.info
        
        return {
            "company_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "summary": info.get("longBusinessSummary"),
            "metrics": {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "roe": info.get("returnOnEquity"),
                "debt_to_equity": info.get("debtToEquity")
            },
            # Basic Balance Sheet Summary
            "balance_sheet": ticker.balance_sheet.to_dict() if not ticker.balance_sheet.empty else None,
            "quarterly_results": ticker.quarterly_financials.iloc[:, 0].to_dict() if not ticker.quarterly_financials.empty else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sourcing financials: {str(e)}")