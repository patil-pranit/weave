import requests

def get_nse_stock_price(symbol: str):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = { "user-agent": "Mozilla/5.0" }
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    return float(data["priceInfo"]["lastPrice"])