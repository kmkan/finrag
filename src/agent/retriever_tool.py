from langchain_core.tools import tool
from etl.embed import get_model
from etl.store import get_collection

VECTORS_WANTED = 5


@tool
def search_financial_news(query):
    model = get_model()
    query_embedding = model.encode([query])[0].tolist()

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=VECTORS_WANTED,
    )

    if not results['documents'][0]:
        return 'No relevant articles found.'

    formatted = []
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        formatted.append(
            f'[Source: {meta['title']} ({meta['source']})]\n{doc}'
        )

    return ''.join(formatted)
