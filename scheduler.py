# scheduler.py
import schedule
import time
from datetime import datetime
from cnn_scraper import run_scraper
from db import clear_old_news


def scheduled_job():
    """Задача для планировщика."""
    try:
        run_scraper()
        # Очищаем новости старше 7 дней
        clear_old_news(days=7)
    except Exception as e:
        print(f"❌ Scheduled job failed: {e}")


def run_scheduler():
    """Запускает планировщик."""
    print(f"\n{'=' * 60}")
    print("⏰ Scheduler started")
    print(f"📅 News will be updated every 3 hours")
    print(f"🗑️  Old news (>7 days) will be auto-cleaned")
    print(f"{'=' * 60}\n")

    # Запускаем сразу при старте
    scheduled_job()

    # Планируем каждые 3 часа
    schedule.every(3).hours.do(scheduled_job)

    # Также можно добавить расписание по времени
    schedule.every().day.at("00:00").do(scheduled_job)
    schedule.every().day.at("06:00").do(scheduled_job)
    schedule.every().day.at("12:00").do(scheduled_job)
    schedule.every().day.at("18:00").do(scheduled_job)

    print("✅ Initial scrape complete. Waiting for next scheduled run...\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n⏹️  Scheduler stopped by user")