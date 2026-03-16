from flask import Flask, jsonify, request, render_template
import json
import os
from datetime import datetime
from db import init_db, get_news, get_stats

app = Flask(__name__)

# Инициализация БД при запуске
init_db()


@app.route('/')
def index():
    """Отдаёт главный HTML шаблон."""
    return render_template('index.html')


@app.route('/api/news')
def get_news_api():
    """API endpoint для получения новостей из БД."""
    category = request.args.get('category', default=None)
    query = request.args.get('q', default='')
    limit = request.args.get('limit', default=50, type=int)

    if query:
        from db import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM news 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY date DESC 
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            news = [dict(row) for row in cursor.fetchall()]
    else:
        news = get_news(limit=limit, category=category)

    print(f"📡 API: Returning {len(news)} news articles")  # Для отладки
    return jsonify(news)


@app.route('/api/stats')
def get_stats_api():
    """API endpoint для статистики."""
    stats = get_stats()
    return jsonify(stats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)