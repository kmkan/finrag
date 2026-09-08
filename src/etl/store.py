import hashlib
import chromadb
from etl.fetch import fetch_all
from etl.chunk import process_article
from etl.embed import embed_chunks

DB_PATH = 'data/chroma'
COLLECTION_NAME = 'news'

client = None

def get_client() -> chromadb.PersistentClient:
    global client
    if client == None:
        client = chromadb.PersistentClient(path=DB_PATH)
    return client


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def _make_id(chunk):
    raw = f'{chunk['url']}::{chunk['chunk_index']}'
    return hashlib.sha256(raw.encode()).hexdigest()


def store_chunks(chunks) -> int:
    collection = get_collection()

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(_make_id(chunk))
        embeddings.append(chunk['embedding'])
        documents.append(chunk['chunk_text'])
        metadatas.append({
            'source': chunk['source'],
            'title': chunk['title'],
            'url': chunk['url'],
            'chunk_index': chunk['chunk_index'],
            'published': str(chunk['published']) if chunk['published'] else '',
        })

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(ids)


if __name__ == '__main__':
    articles = fetch_all()
    chunks = []
    for article in articles:
        chunks.extend(process_article(article))

    embedded = embed_chunks(chunks)
    count = store_chunks(embedded)

    print(f'Chunks: {count}')

    collection = get_collection()
    print(f'Chunks in collection: {collection.count()}')