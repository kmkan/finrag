import time
from datetime import datetime, timedelta

from etl.fetch_finnhub import TICKERS, fetch_company_news
from etl.scrape import enrich_articles
from etl.chunk import process_article
from etl.embed import embed_chunks
from etl.store import store_chunks, get_collection

MONTHS_BACK = 12
REQUEST_DELAY = 1.0


def month_ranges(months_back):
    ranges = []
    today = datetime.now()
    for i in range(months_back):
        end = today - timedelta(days=30 * i)
        start = end - timedelta(days=30)
        ranges.append((start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
    return ranges


def run_backfill():
    ranges = month_ranges(MONTHS_BACK)
    total_stored = 0

    for ticker in TICKERS:
        print(f'=== {ticker} ===')
        ticker_articles = []

        for from_date, to_date in ranges:
            try:
                articles = fetch_company_news(ticker, from_date, to_date)
                ticker_articles.extend(articles)
                print(f'  {from_date} to {to_date}: {len(articles)} articles')
            except Exception as e:
                print(f'  {from_date} to {to_date}: FAILED ({e})')
            time.sleep(REQUEST_DELAY)

        if not ticker_articles:
            continue

        print(f'  Scraping {len(ticker_articles)} articles...')
        enriched = enrich_articles(ticker_articles)

        chunks = []
        for article in enriched:
            chunks.extend(process_article(article))

        embedded = embed_chunks(chunks)
        stored = store_chunks(embedded)
        total_stored += stored
        print(f'  Stored {stored} chunks for {ticker}')

    total = get_collection().count()
    print(f'Backfill complete. Stored {total_stored} chunks this run. Collection total: {total}')


if __name__ == '__main__':
    run_backfill()