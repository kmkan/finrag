import os
import time
import requests
from datetime import datetime, timedelta

FINNHUB_BASE = 'https://finnhub.io/api/v1'
REQUEST_DELAY = 1.0  

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX",
    "AMD", "INTC", "JPM", "BAC", "XOM", "CVX", "JNJ", "PFE", "DIS", "BA",
]


def _get_api_key() -> str:
    key = os.environ.get('FINNHUB_API_KEY')
    if not key:
        raise ValueError('FINNHUB_API_KEY not set in environment/.env')
    return key


def _normalize_article(raw: dict, ticker: str | None) -> dict:
    published = None
    if raw.get('datetime'):
        published = datetime.fromtimestamp(raw["datetime"])

    return {
        "source": raw.get("source", "finnhub"),
        "title": raw.get("headline", "").strip(),
        "url": raw.get("url", ""),
        "content": raw.get("summary") or raw.get("headline", ""),
        "published": published,
        "ticker": ticker,
    }


def fetch_company_news(ticker: str, from_date: str, to_date: str) -> list[dict]:
    response = requests.get(
        f"{FINNHUB_BASE}/company-news",
        params={
            "symbol": ticker,
            "from": from_date,
            "to": to_date,
            "token": _get_api_key(),
        },
        timeout=10,
    )
    response.raise_for_status()
    raw_articles = response.json()
    return [_normalize_article(a, ticker) for a in raw_articles]


def fetch_general_news() -> list[dict]:
    response = requests.get(
        f"{FINNHUB_BASE}/news",
        params={"category": "general", "token": _get_api_key()},
        timeout=10,
    )
    response.raise_for_status()
    raw_articles = response.json()
    return [_normalize_article(a, None) for a in raw_articles]


def fetch_incremental(days_back: int = 2) -> list[dict]:
    """For the daily cron: recent news per tracked ticker, plus general market news."""
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    all_articles = fetch_general_news()

    for ticker in TICKERS:
        articles = fetch_company_news(ticker, from_date, to_date)
        all_articles.extend(articles)
        time.sleep(REQUEST_DELAY)

    return all_articles


if __name__ == "__main__":
    articles = fetch_company_news("AAPL", "2026-08-01", "2026-09-01")
    print(f"Fetched {len(articles)} AAPL articles")
    if articles:
        print(articles[0])