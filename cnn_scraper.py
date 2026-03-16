import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
from classifier import classify_articles
from db import init_db, insert_news


def parse_cnn_lite():
    """Parses the CNN Lite website to extract latest news stories."""
    url = "https://lite.cnn.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching the page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем все ссылки с классом card--lite
    articles = []

    for link in soup.find_all('a', href=True):
        # Проверяем, находится ли ссылка внутри li.card--lite
        parent_li = link.find_parent('li', class_='card--lite')
        if not parent_li:
            continue

        title = link.get_text(strip=True)
        relative_url = link.get('href', '').strip()

        if not title or not relative_url:
            continue

        # Формируем полный URL
        if relative_url.startswith('/'):
            full_url = f"https://lite.cnn.com{relative_url}"
        elif relative_url.startswith('http'):
            full_url = relative_url
        else:
            full_url = f"https://lite.cnn.com/{relative_url}"

        # Генерируем уникальный ID
        unique_id = abs(hash(full_url)) % (10 ** 8)

        article = {
            "id": unique_id,
            "title": title,
            "description": title,
            "category": "International",
            "source": "CNN Lite",
            "date": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "imageUrl": "",
            "url": full_url
        }
        articles.append(article)

    return articles


def run_scraper():
    """Запускает полный цикл парсинга, классификации и сохранения."""
    print(f"\n{'=' * 60}")
    print(f"🔄 Starting news scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    # Инициализация БД
    init_db()

    # Парсинг
    print("🕷️  Parsing CNN Lite...")
    parsed_news = parse_cnn_lite()

    if not parsed_news:
        print("❌ No news articles were parsed.")
        return 0

    # Классификация
    print(f"🏷️  Classifying {len(parsed_news)} articles...")
    classified_news = classify_articles(parsed_news)

    # Сохранение в БД
    print("💾 Saving to database...")
    inserted = insert_news(classified_news)

    # Статистика по категориям
    category_stats = {}
    for article in classified_news:
        cat = article['category']
        category_stats[cat] = category_stats.get(cat, 0) + 1

    print(f"\n✅ Successfully processed {len(parsed_news)} articles")
    print(f"✅ Inserted {inserted} new articles into database")
    print(f"\n📊 Category distribution:")
    for cat, count in sorted(category_stats.items()):
        print(f"   • {cat}: {count}")
    print(f"{'=' * 60}\n")

    return inserted


if __name__ == "__main__":
    run_scraper()