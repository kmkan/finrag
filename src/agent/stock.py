import os
import requests
from langchain_core.tools import tool

FINNHUB_BASE = 'https://finnhub.io/api/v1'


def _get_api_key():
    key = os.environ.get('FINNHUB_API_KEY')
    if not key:
        raise ValueError('FINNHUB_API_KEY not set in environment/.env')
    return key


@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price and recent performance for a given ticker symbol.
    Use this when the user asks about a specific stock's price, how it's trading,
    or its recent performance. Requires a ticker symbol (e.g. AAPL, TSLA, GOOGL),
    not a company name."""

    try:
        response = requests.get(
            f'{FINNHUB_BASE}/quote',
            params={'symbol': ticker.upper(), 'token': _get_api_key()},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f'Error fetching data for ticker {ticker}: {e}'

    price = data.get('c')
    if not price:
        return f"Could not find price data for ticker '{ticker}'. It may be an invalid symbol."

    prev_close = data.get('pc')
    change = data.get('d')
    change_pct = data.get('dp')
    day_low = data.get('l')
    day_high = data.get('h')

    summary = f'{ticker.upper()}: {price:.2f} USD'
    if change is not None and change_pct is not None:
        direction = 'up' if change >= 0 else 'down'
        summary += f', {direction} {abs(change):.2f} ({abs(change_pct):.2f}%) from previous close'

    if day_low and day_high:
        summary += f'. Day range: {day_low:.2f}-{day_high:.2f}'

    return summary