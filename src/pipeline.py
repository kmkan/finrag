from etl.fetch_finnhub import fetch_incremental
from etl.chunk import process_article
from etl.embed import embed_chunks
from etl.store import store_chunks, get_collection
from etl.scrape import enrich_articles

def run():
    articles = fetch_incremental(days_back=2)
    articles = enrich_articles(articles)
    chunks = []
    
    for article in articles:
        chunks.extend(process_article(article))
        
    embedded = embed_chunks(chunks)
    stored = store_chunks(embedded)
    print(f'Pipeline ran successfully. Stored {stored} chunks. Chunks in collection: {get_collection().count()}.')

if __name__ == '__main__':
    run()