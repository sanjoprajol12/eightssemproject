"""
scripts/fetch_today.py
======================
Redesigned automated daily news ingestion script.
- Fetches breaking news from BBC and NewsAPI (if configured)
- Validates article fields
- Enforces SHA-256 duplicate detection before inserting
- Inserts directly into SQLite FTS5 IndexedNews
- Runs incremental partial_fit on SGDClassifier
- Does NOT append raw data to True.csv
- Safe to re-run multiple times a day without duplicates
- Structured logging
"""

import os
import sys
import datetime
import logging
import requests
from bs4 import BeautifulSoup

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FakeNewsDetect.settings')

import django
django.setup()

import joblib
import numpy as np
from detection.models import IndexedNews
from sklearn.feature_extraction.text import HashingVectorizer

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in fetch_today: %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback default key or environment variable
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', 'ec984d63232e45e4a02a447d8e1e8c30')
MODEL_DIR = os.path.join(BASE_DIR, 'ml_models', 'current')


def fetch_bbc_headlines() -> list:
    """Fetch headlines from BBC News RSS/Homepage."""
    articles = []
    try:
        url = "https://www.bbc.com/news"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TruthLens/2.0'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for h in soup.find_all(['h2', 'h3']):
                title = h.get_text(strip=True)
                if title and len(title.split()) >= 4 and len(title) > 20:
                    articles.append({
                        'title': title,
                        'summary': '',
                        'source': 'BBC News',
                        'published_at': datetime.datetime.now(datetime.timezone.utc)
                    })
            logger.info(f"Fetched {len(articles)} headlines from BBC News.")
    except Exception as e:
        logger.warning(f"BBC fetch error: {e}")
    return articles


def fetch_newsapi_headlines(api_key: str, max_items: int = 50) -> list:
    """Fetch breaking news via NewsAPI."""
    articles = []
    if not api_key:
        return articles

    try:
        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'language': 'en',
            'pageSize': min(max_items, 100),
            'apiKey': api_key
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get('articles', []):
                title = item.get('title')
                desc = item.get('description') or ''
                src_name = item.get('source', {}).get('name') or 'NewsAPI'
                pub_date = item.get('publishedAt')

                if title and len(title.split()) >= 4:
                    articles.append({
                        'title': title,
                        'summary': desc[:300] if desc else '',
                        'source': src_name,
                        'published_at': datetime.datetime.now(datetime.timezone.utc)
                    })
            logger.info(f"Fetched {len(articles)} headlines from NewsAPI.")
        else:
            logger.info(f"NewsAPI responded with status {r.status_code}: {r.text[:120]}")
    except Exception as e:
        logger.warning(f"NewsAPI fetch error: {e}")
    return articles


def update_incremental_model(new_texts: list, label_val: int = 1):
    """Update online SGDClassifier via partial_fit without loading entire dataset."""
    sgd_path = os.path.join(MODEL_DIR, 'sgd_logistic.pkl')
    if not os.path.exists(sgd_path) or not new_texts:
        return

    try:
        sgd = joblib.load(sgd_path)
        vectorizer = HashingVectorizer(n_features=2**16, alternate_sign=False, norm='l2', ngram_range=(1, 2))
        X = vectorizer.transform(new_texts)
        y = np.full(len(new_texts), label_val, dtype=int)
        sgd.partial_fit(X, y)
        joblib.dump(sgd, sgd_path)
        logger.info(f"Incrementally updated SGDClassifier with {len(new_texts)} new samples.")
    except Exception as e:
        logger.warning(f"Failed to update incremental model: {e}")


def ingest_today():
    start_time = datetime.datetime.now()
    logger.info("Starting daily news ingestion pipeline...")

    candidates = []
    candidates.extend(fetch_bbc_headlines())
    candidates.extend(fetch_newsapi_headlines(NEWS_API_KEY))

    if not candidates:
        logger.warning("No candidate articles retrieved. Ingestion finished.")
        return

    # Filter and deduplicate against database
    inserted_count = 0
    new_trained_texts = []

    for item in candidates:
        title = item['title'].strip()
        summary = item.get('summary', '').strip()
        source = item.get('source', 'Daily Feed')
        pub_date = item.get('published_at')

        # Validate
        if len(title) < 15 or len(title.split()) < 4:
            continue

        chash = IndexedNews.compute_hash(title, summary)
        # Check if already indexed
        if IndexedNews.objects.filter(content_hash=chash).exists():
            continue

        try:
            IndexedNews.objects.create(
                title=title[:500],
                summary=summary,
                source=source,
                label='real',
                published_at=pub_date,
                content_hash=chash,
                is_verified=False # Daily transient article subject to 30-day retention
            )
            inserted_count += 1
            new_trained_texts.append(f"{title} {summary}")
        except Exception as e:
            logger.warning(f"Skipping malformed article '{title[:40]}': {e}")

    logger.info(f"Successfully inserted {inserted_count} new deduplicated articles into SQLite index.")

    # Incremental online learning update
    if new_trained_texts:
        update_incremental_model(new_trained_texts, label_val=1)

    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    logger.info(f"Ingestion completed in {elapsed:.2f}s. (Duplicates skipped: {len(candidates) - inserted_count})")


if __name__ == '__main__':
    ingest_today()
