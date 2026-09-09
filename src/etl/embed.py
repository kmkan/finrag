from sentence_transformers import SentenceTransformer

MODAL_NAME = 'all-MiniLM-L6-v2'
MODAL = None

def get_model():
    global MODAL
    if MODAL == None:
        MODAL = SentenceTransformer(MODAL_NAME)
    return MODAL

def embed_chunks(chunks):
    model = get_model()
    texts = [chunk['chunk_text'] for chunk in chunks]

    embeddings = model.encode(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk['embedding'] = embedding.tolist()

    return chunks

if __name__ == '__main__':
    from fetch import fetch_all
    from chunk import process_article   
    articles = fetch_all()
    chunks = []
    for article in articles:
        chunks.extend(process_article(article))

    embeddings = embed_chunks(chunks)
    print(f'There are {len(embeddings)} embeddings.')
    print(f'Examples: {embeddings[0]['embedding'][:5]}')