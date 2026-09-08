from bs4 import BeautifulSoup
from fetch import fetch_all

CHUNK_SIZE = 200
CHUNK_OVERLAP = 40

def clean_html(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    text = soup.get_text(separator=' ')
    return ' '.join(text.split())

def chunk_text(text, chunk_size = CHUNK_SIZE, overlap = CHUNK_OVERLAP):
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

def process_article(article):
    cleaned = clean_html(article['content'])
    text_chunks = chunk_text(cleaned)

    chunked_articles = []
    for i, chunk in enumerate(text_chunks):
        chunked_articles.append({
            'chunk_text': chunk,
            'chunk_index': i,
            'source': article['source'],
            'title': article['title'],
            'url': article['url'],
            'published': article['published'],
        })
    return chunked_articles

if __name__ == '__main__':
    articles = fetch_all()
    chunks = []
    for article in articles:
        chunks.extend(process_article(article))
    chunk_count = len(chunks)
    print(f'Created {chunk_count} chunks.')
    if chunks:
        print(f'Example: {chunks[0]}')