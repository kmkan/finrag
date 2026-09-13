from datetime import datetime, timedelta

from etl.fetch_finnhub import fetch_company_news
from etl.scrape import enrich_articles
from etl.chunk import process_article
from etl.embed import embed_chunks
from etl.store import store_chunks, get_collection

TICKER = 'AAPL'
DAYS_BACK = 1

to_date = datetime.now().strftime('%Y-%m-%d')
from_date = (datetime.now() - timedelta(days=DAYS_BACK)).strftime('%Y-%m-%d')

print(f'Fetching {TICKER} news from {from_date} to {to_date}...')
articles = fetch_company_news(TICKER, from_date, to_date)
print(f'  Got {len(articles)} articles')

print('Scraping...')
enriched = enrich_articles(articles)

print('Chunking...')
chunks = []
for article in enriched:
    chunks.extend(process_article(article))
print(f'  Produced {len(chunks)} chunks')

print('Embedding...')
embedded = embed_chunks(chunks)

print('Storing...')
stored = store_chunks(embedded)

total = get_collection().count()
print(f'Done. Stored {stored} chunks. Collection total: {total}')