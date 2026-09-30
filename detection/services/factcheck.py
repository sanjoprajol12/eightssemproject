import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

FACT_CHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def query_google_fact_check(query_text: str) -> dict:
    """
    Query Google Fact Check Tools API for verified claims.
    Optional external verification layer that fails safely and gracefully
    when offline or when credentials are not configured.
    """
    api_key = getattr(settings, 'GOOGLE_FACT_CHECK_API_KEY', '')
    if not api_key:
        return {
            'available': False,
            'reason': 'API key not configured',
            'matched': False,
            'claims': []
        }

    query = (query_text or "").strip()
    if not query:
        return {'available': True, 'matched': False, 'claims': []}

    # Shorten query to first 120 chars to avoid URL length issues
    search_query = query[:120]

    try:
        response = requests.get(
            FACT_CHECK_URL,
            params={
                'query': search_query,
                'key': api_key,
                'languageCode': 'en'
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            claims_data = data.get('claims', [])
            if not claims_data:
                return {
                    'available': True,
                    'matched': False,
                    'claims': [],
                    'source': 'Google Fact Check Tools'
                }

            processed = []
            for c in claims_data[:3]:
                claim_text = c.get('text', '')
                claimant = c.get('claimant', 'Unknown')
                reviews = c.get('claimReview', [])
                review_list = []
                for r in reviews:
                    publisher = r.get('publisher', {}).get('name', 'Fact Checker')
                    rating = r.get('textualRating', 'Unrated')
                    url = r.get('url', '')
                    review_list.append({
                        'publisher': publisher,
                        'rating': rating,
                        'url': url
                    })
                processed.append({
                    'text': claim_text,
                    'claimant': claimant,
                    'reviews': review_list
                })

            return {
                'available': True,
                'matched': True,
                'claims': processed,
                'source': 'Google Fact Check Tools'
            }
        else:
            logger.info(f"Google Fact Check API responded with status {response.status_code}")
            return {
                'available': False,
                'reason': f"HTTP status {response.status_code}",
                'matched': False,
                'claims': []
            }
    except Exception as e:
        logger.warning(f"Google Fact Check API query failed: {e}")
        return {
            'available': False,
            'reason': str(e),
            'matched': False,
            'claims': []
        }
