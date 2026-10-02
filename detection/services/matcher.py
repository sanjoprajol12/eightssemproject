import re
import logging
from django.db import connection
from detection.models import IndexedNews
try:
    from apps.cms.models import NewsAndUpdate
except ImportError:
    NewsAndUpdate = None

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


def _content_tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r'[a-zA-Z0-9]+', text or '')
        if len(token) > 2
    }


class NewsMatcher:
    """
    High-speed evidence matcher that replaces full CSV scans.
    Performs:
    1. Exact / Partial match against the Article / News database table.
    2. Instantaneous SHA-256 hash match against IndexedNews.
    3. FTS5 BM25 ranked search against indexed historical news corpus.
    """

    @staticmethod
    def match_article_table(text: str) -> dict:
        """
        Check verified CMS NewsAndUpdate and historical article tables.
        """
        stripped = (text or "").strip()
        if not stripped:
            return {'matched': False}

        # 1. Match NewsAndUpdate in CMS
        if NewsAndUpdate is not None:
            try:
                exact = NewsAndUpdate.objects.filter(title__iexact=stripped, is_active=True).first()
                if exact:
                    return {
                        'matched': True,
                        'match_type': 'article_table_exact',
                        'title': exact.title,
                        'label': 'real',
                        'source': 'Verified News & Updates (CMS)',
                        'score': 1.0,
                        'article_id': exact.id
                    }
                if len(stripped) >= 15:
                    partial = NewsAndUpdate.objects.filter(title__icontains=stripped[:60], is_active=True).first()
                    if partial:
                        return {
                            'matched': True,
                            'match_type': 'article_table_partial',
                            'title': partial.title,
                            'label': 'real',
                            'source': 'Verified News & Updates (CMS Partial)',
                            'score': 0.85,
                            'article_id': partial.id
                        }
            except Exception as e:
                logger.warning(f"Error querying NewsAndUpdate: {e}")

        # 2. Check accounts_article table if present
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_article';")
                if cursor.fetchone():
                    cursor.execute("SELECT id, title FROM accounts_article WHERE LOWER(title) = LOWER(%s) LIMIT 1;", [stripped])
                    row = cursor.fetchone()
                    if row:
                        return {
                            'matched': True,
                            'match_type': 'article_table_exact',
                            'title': row[1],
                            'label': 'real',
                            'source': 'Verified Article Database (Exact)',
                            'score': 1.0,
                            'article_id': row[0]
                        }
        except Exception as e:
            logger.warning(f"Error querying accounts_article table: {e}")

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
                        # BM25 rank is only useful when the returned document also
                        # covers the query terms; OR queries otherwise match common words.
                        query_tokens = _content_tokens(stripped)
                        document_tokens = _content_tokens(f'{title} {summary}')
                        overlap = len(query_tokens & document_tokens) / max(len(query_tokens), 1)
                        rank_score = abs(float(rank)) / (abs(float(rank)) + 1.0)
                        norm_score = round((rank_score + overlap) / 2.0, 3)

                        return {
                            'matched': True,
                            'match_type': 'fts5_bm25',
                            'title': title,
                            'summary': summary[:200] if summary else '',
                            'source': source or 'Indexed News Corpus',
                            'label': label,
                            'score': norm_score,
                            'bm25_rank': round(float(rank), 4),
                            'bm25_score': round(rank_score, 3),
                            'overlap_score': round(overlap, 3),
                            'match_strength': 'strong' if rank_score > 0.75 and overlap > 0.85 else 'weak',
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
