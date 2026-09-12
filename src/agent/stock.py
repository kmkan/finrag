import yfinance as yf
from langchain_core.tools import tool


@tool
def get_stock_price(ticker):
    '''Get the current stock price and recent performance for a given ticker symbol.
    Use this when the user asks about a specific stock's price, how it's trading,
    or its recent performance. Requires a ticker symbol (e.g. AAPL, TSLA, GOOGL),
    not a company name.'''

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if price is None:
            return f"Could not find price data for ticker '{ticker}'. It may be an invalid symbol."

        prev_close = info.get('previousClose')
        change = None
        change_pct = None
        if prev_close:
            change = price - prev_close
            change_pct = (change / prev_close) * 100

        name = info.get('longName', ticker)
        currency = info.get('currency', 'USD')

        summary = f'{name} ({ticker.upper()}): {price:.2f} {currency}'
        if change is not None:
            direction = 'up' if change >= 0 else 'down'
            summary += f', {direction} {abs(change):.2f} ({abs(change_pct):.2f}%) from previous close'

        day_low = info.get('dayLow')
        day_high = info.get('dayHigh')
        if day_low and day_high:
            summary += f'. Day range: {day_low:.2f}-{day_high:.2f}'

        week52_low = info.get('fiftyTwoWeekLow')
        week52_high = info.get('fiftyTwoWeekHigh')
        if week52_low and week52_high:
            summary += f'. 52-week range: {week52_low:.2f}-{week52_high:.2f}'

        return summary

    except Exception as e:
        return f"Error fetching data for ticker '{ticker}': {e}"
