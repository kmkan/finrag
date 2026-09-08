from etl.fetch import fetch_all
from etl.chunk import process_article
from etl.embed import embed_chunks
from etl.store import store_chunks, get_collection

def run():
    articles = fetch_all()
    chunks = []
    
    for article in articles:
        chunks.extend(process_article(article))
        
    embedded = embed_chunks(chunks)
    stored = store_chunks(embedded)
    print(f'Pipeline ran successfully. Stored {stored} chunks. Chunks in collection: {get_collection().count()}.')

if __name__ == '__main__':
    run()