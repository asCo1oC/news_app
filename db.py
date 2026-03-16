# db.py
import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = 'news.db'


@contextmanager
def get_db_connection():
    """Контекстный менеджер для подключения к БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Инициализация таблицы news."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'International',
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                imageUrl TEXT,
                url TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_news_date ON news(date DESC)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_news_category ON news(category)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_news_url ON news(url)')
        conn.commit()


def insert_news(articles: list) -> int:
    """
    Вставляет новости в БД, пропуская дубликаты по URL.
    Возвращает количество добавленных записей.
    """
    inserted = 0
    with get_db_connection() as conn:
        for article in articles:
            try:
                conn.execute('''
                    INSERT OR IGNORE INTO news 
                    (id, title, description, category, source, date, imageUrl, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['id'],
                    article['title'],
                    article.get('description', article['title']),
                    article.get('category', 'International'),
                    article.get('source', 'CNN Lite'),
                    article['date'],
                    article.get('imageUrl', ''),
                    article['url']
                ))
                if conn.total_changes > 0:
                    inserted += 1
            except sqlite3.IntegrityError:
                continue
        conn.commit()
    return inserted


def get_news(limit: int = 50, category: str = None) -> list:
    """Получает новости из БД с опциональной фильтрацией по категории."""
    with get_db_connection() as conn:
        if category and category.lower() != 'all':
            cursor = conn.execute('''
                SELECT * FROM news 
                WHERE LOWER(category) = LOWER(?)
                ORDER BY date DESC 
                LIMIT ?
            ''', (category, limit))
        else:
            cursor = conn.execute('''
                SELECT * FROM news 
                ORDER BY date DESC 
                LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_all_news() -> list:
    """Получает все новости из БД."""
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM news ORDER BY date DESC')
        return [dict(row) for row in cursor.fetchall()]


def get_stats() -> dict:
    """Получает статистику по категориям."""
    with get_db_connection() as conn:
        total = conn.execute('SELECT COUNT(*) FROM news').fetchone()[0]
        categories = conn.execute('''
            SELECT category, COUNT(*) as count 
            FROM news 
            GROUP BY category
        ''').fetchall()

        today = datetime.utcnow().strftime('%Y-%m-%d')
        today_count = conn.execute('''
            SELECT COUNT(*) FROM news 
            WHERE date LIKE ?
        ''', (f'{today}%',)).fetchone()[0]

    return {
        'total': total,
        'today': today_count,
        'by_category': {row['category']: row['count'] for row in categories}
    }


def clear_old_news(days: int = 7):
    """Удаляет новости старше указанного количества дней."""
    with get_db_connection() as conn:
        cutoff_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        conn.execute('''
            DELETE FROM news 
            WHERE date < datetime('now', ?)
        ''', (f'-{days} days',))
        conn.commit()