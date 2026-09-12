from langchain_core.tools import tool
from etl.embed import get_model
from etl.store import get_collection

N_VECTORS = 5


@tool
def search_financial_news(query: str) -> str:
    """Search recent financial news articles for information relevant to a query.
    Use this when you need current market news, company-specific events,
    or recent financial developments to answer a question."""

    model = get_model()
    query_embedding = model.encode([query])[0].tolist()

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=N_VECTORS,
    )

    if not results['documents'][0]:
        return "No relevant articles found."

    formatted = []
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        formatted.append(
            f"[Source: {meta['title']} ({meta['source']})]\n{doc}"
        )

    return "\n\n".join(formatted)
