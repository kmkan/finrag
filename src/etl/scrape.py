import time
import requests
import trafilatura

USER_AGENT = 'Mozilla/5.0 (personal project)'


def scrape_article(url: str) -> str | None:
    try:
        response = requests.get(
            url,
            headers={'User-Agent': USER_AGENT},
            timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'{url}: {e}')
        return None

    return trafilatura.extract(response.text)


def enrich_articles(articles: list[dict]) -> list[dict]:
    for article in articles:
        scraped_text = scrape_article(article['url'])
        if scraped_text:
            article['content'] = scraped_text
        time.sleep(1)

    return articles


if __name__ == '__main__':
    from fetch import fetch_all
    articles = fetch_all()[:3]
    enriched = enrich_articles(articles)

    for a in enriched:
        print(f'{a['title']}')
        print(f'{a['content'][:200]}')