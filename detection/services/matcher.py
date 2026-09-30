import re
import logging
from django.db import connection
from detection.models import IndexedNews
from accounts.models import Article

logger = logging.getLogger(__name__)


def sanitize_fts_query(query: str) -> str:
    """
    Sanitize user input to be safely passed to SQLite FTS5 MATCH.
    Extracts alphanumeric keywords and wraps them in double quotes or joins with OR.
    """
    tokens = re.findall(r'[a-zA-Z0-9]+', query)
    if not tokens:
        return ""
    # Filter very short words
    filtered = [t for t in tokens if len(t) > 2]
    if not filtered:
        filtered = tokens
    # Take first 10 most relevant keywords to prevent query bloat
    keywords = filtered[:10]
    return " OR ".join(f'"{kw}"' for kw in keywords)


class NewsMatcher:
    """
    High-speed evidence matcher that replaces full CSV scans.
    Performs:
    1. Exact / Partial match against the Article database table.
    2. Instantaneous SHA-256 hash match against IndexedNews.
    3. FTS5 BM25 ranked search against indexed historical news corpus.
    """

    @staticmethod
    def match_article_table(text: str) -> dict:
        """
        Check existing accounts.Article database table.
        """
        stripped = (text or "").strip()
        if not stripped:
            return {'matched': False}

        # 1. Case-insensitive exact title match
        try:
            exact = Article.objects.filter(title__iexact=stripped).first()
            if exact:
                return {
                    'matched': True,
                    'match_type': 'article_table_exact',
                    'title': exact.title,
                    'label': 'real',
                    'source': 'Admin Article Database (Exact)',
                    'score': 1.0,
                    'article_id': exact.id
                }
        except Exception as e:
            logger.warning(f"Error querying Article table exact: {e}")

        # 2. Case-insensitive contains match (for reasonably long queries)
        if len(stripped) >= 15:
            try:
                partial = Article.objects.filter(title__icontains=stripped).first()
                if not partial:
                    # Also check if article title is inside stripped text
                    # (e.g. user pasted full article text with title headline at start)
                    partial = Article.objects.filter(description__icontains=stripped[:100]).first()

                if partial:
                    return {
                        'matched': True,
                        'match_type': 'article_table_partial',
                        'title': partial.title,
                        'label': 'real',
                        'source': 'Admin Article Database (Partial)',
                        'score': 0.85,
                        'article_id': partial.id
                    }
            except Exception as e:
                logger.warning(f"Error querying Article table partial: {e}")

        return {'matched': False}

    @staticmethod
    def match_indexed_corpus(text: str) -> dict:
        """
        Check SQLite FTS5 news index using BM25 ranking, plus SHA-256 hash check.
        Replaces loading True.csv and Fake.csv into RAM.
        """
        stripped = (text or "").strip()
        if not stripped:
            return {'matched': False}

        # 1. Instant SHA-256 content hash lookup
        content_hash = IndexedNews.compute_hash(stripped)
        exact_hash = IndexedNews.objects.filter(content_hash=content_hash).first()
        if exact_hash:
            return {
                'matched': True,
                'match_type': 'index_hash_exact',
                'title': exact_hash.title,
                'label': exact_hash.label, # 'real' or 'fake'
                'source': exact_hash.source,
                'score': 1.0,
                'summary': exact_hash.summary[:200] if exact_hash.summary else ''
            }

        # 2. SQLite FTS5 Full-Text Search with BM25
        fts_query = sanitize_fts_query(stripped)
        if fts_query and connection.vendor == 'sqlite':
            try:
                with connection.cursor() as cursor:
                    # rank in FTS5 is negative (more negative = better match)
                    cursor.execute("""
                        SELECT rowid, title, summary, source, label, rank
                        FROM news_index_fts
                        WHERE news_index_fts MATCH %s
                        ORDER BY rank ASC
                        LIMIT 5;
                    """, [fts_query])
                    rows = cursor.fetchall()

                    if rows:
                        top = rows[0]
                        rowid, title, summary, source, label, rank = top
                        # Normalize rank: SQLite FTS5 rank typically between -0.01 and -20.0
                        # Convert to 0.0 - 1.0 confidence proxy
                        norm_score = round(min(1.0, max(0.5, abs(rank) / 10.0)), 2)

                        return {
                            'matched': True,
                            'match_type': 'fts5_bm25',
                            'title': title,
                            'summary': summary[:200] if summary else '',
                            'source': source or 'Indexed News Corpus',
                            'label': label,
                            'score': norm_score,
                            'total_candidates': len(rows)
                        }
            except Exception as e:
                logger.warning(f"FTS5 match error: {e}")

        # 3. Fallback: ILIKE / icontains on IndexedNews model if query is specific
        if len(stripped) >= 20:
            sub = IndexedNews.objects.filter(title__icontains=stripped[:60]).first()
            if sub:
                return {
                    'matched': True,
                    'match_type': 'index_title_contains',
                    'title': sub.title,
                    'summary': sub.summary[:200] if sub.summary else '',
                    'source': sub.source,
                    'label': sub.label,
                    'score': 0.80
                }

        return {'matched': False}
