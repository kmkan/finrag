import feedparser
from datetime import datetime
from dateutil import parser as date_parser

FEEDS = {
    'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
    'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
}

def fetch_feed(source_name, url):
    parsed = feedparser.parse(url)
    articles = []
    for entry in parsed.entries:
        articles.append({
            'source': source_name,
            'title': entry.get('title', '').strip(),
            'url': entry.get('link', ''),
            'content': _extract_content(entry),
            'published': _parse_date(entry.get('published')),
        })
    return articles

def _extract_content(entry):
    for field in ('summary', 'description'):
        value = entry.get(field)
        if value:
            return value
    return entry.get('title', '')

def _parse_date(date):
    if not date:
        return None
    try:
        return date_parser.parse(date)
    except (ValueError, TypeError):
        return None

def fetch_all():
    all_articles = []
    for source_name, url in FEEDS.items():
        all_articles.extend(fetch_feed(source_name, url))
    return all_articles

if __name__ == '__main__':
    articles = fetch_all()
    print(f'Fetched {len(articles)} articles.')
    for a in articles:
        print(f'[{a['source']}] {a['title']} {a['content']}')
    