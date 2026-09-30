import re
import ipaddress
import socket
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

# Curated list of established major global news and reference outlets
VERIFIED_DOMAINS = {
    'reuters.com': 'Reuters News Agency',
    'apnews.com': 'Associated Press',
    'bbc.com': 'BBC News',
    'bbc.co.uk': 'BBC News',
    'nytimes.com': 'The New York Times',
    'theguardian.com': 'The Guardian',
    'washingtonpost.com': 'The Washington Post',
    'wsj.com': 'The Wall Street Journal',
    'bloomberg.com': 'Bloomberg News',
    'npr.org': 'National Public Radio',
    'aljazeera.com': 'Al Jazeera',
    'dw.com': 'Deutsche Welle',
    'france24.com': 'France 24',
    'nature.com': 'Nature Publishing',
    'scientificamerican.com': 'Scientific American',
    'who.int': 'World Health Organization',
    'cdc.gov': 'Centers for Disease Control',
    'kathmandupost.com': 'The Kathmandu Post',
    'thehimalayantimes.com': 'The Himalayan Times',
    'onlinekhabar.com': 'OnlineKhabar',
}

KNOWN_SATIRE_DOMAINS = {
    'theonion.com': 'The Onion (Satire)',
    'babylonbee.com': 'The Babylon Bee (Satire)',
    'newyorker.com/humor': 'Borowitz Report (Satire)',
    'worldnewsdailyreport.com': 'World News Daily Report (Satire / Hoax)',
    'clickhole.com': 'ClickHole (Satire)',
}


def is_safe_url(url: str) -> bool:
    """
    SSRF Protection: Ensure URL does not point to internal/private IP ranges or loopback.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Disallow loopback and local names
        if hostname.lower() in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
            return False

        # Resolve IP to check for private or reserved subnets
        try:
            ip_str = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_link_local:
                return False
        except Exception:
            return False

        return True
    except Exception:
        return False


def fetch_article_from_url(url: str, timeout: int = 8) -> dict:
    """
    Safely fetch and parse article from URL:
    - SSRF prevention
    - HTML extraction using BeautifulSoup
    - Title and main article text isolation
    """
    if not is_safe_url(url):
        return {
            'success': False,
            'error': 'Invalid or restricted URL. Internal addresses and private networks are prohibited.'
        }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TruthLens/2.0'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        if resp.status_code != 200:
            return {
                'success': False,
                'error': f"Target server returned HTTP status {resp.status_code}."
            }

        # Size limit: read at most 2MB to prevent memory exhaustion
        content = resp.raw.read(2 * 1024 * 1024, decode_content=True)
        soup = BeautifulSoup(content, 'html.parser')

        # Extract title
        title = ""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()

        # Extract paragraphs
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 25]
        text_body = " ".join(paragraphs[:15]) # first 15 paragraphs

        if not title and not text_body:
            return {
                'success': False,
                'error': 'Unable to extract meaningful article text from this web page.'
            }

        parsed = urlparse(resp.url)
        domain = parsed.hostname.lower() if parsed.hostname else ""

        return {
            'success': True,
            'url': resp.url,
            'domain': domain,
            'title': title,
            'text': text_body,
            'is_https': parsed.scheme == 'https'
        }
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Connection timed out while fetching article.'}
    except Exception as e:
        logger.warning(f"Error fetching URL {url}: {e}")
        return {'success': False, 'error': f"Failed to fetch content: {str(e)}"}


def analyze_domain_credibility(domain: str, is_https: bool = True) -> dict:
    """
    Evidence-based domain credibility signals:
    - Known verified publisher
    - Known satirical source
    - HTTPS protocol verification
    - Top level domain signals
    """
    clean_dom = (domain or "").lower()
    if clean_dom.startswith('www.'):
        clean_dom = clean_dom[4:]

    signals = []
    reputation_score = 0.50 # Neutral default

    if is_https:
        signals.append("Uses secure HTTPS connection")
    else:
        signals.append("Insecure HTTP protocol (no TLS encryption)")
        reputation_score -= 0.15

    # Check known verified news outlets
    matched_publisher = None
    for dom_key, pub_name in VERIFIED_DOMAINS.items():
        if clean_dom == dom_key or clean_dom.endswith('.' + dom_key):
            matched_publisher = pub_name
            signals.append(f"Recognized accredited publisher: {pub_name}")
            reputation_score = 0.95
            break

    # Check known satire / parody
    if not matched_publisher:
        for dom_key, sat_name in KNOWN_SATIRE_DOMAINS.items():
            if clean_dom == dom_key or clean_dom.endswith('.' + dom_key):
                signals.append(f"Identified satire / parody publisher: {sat_name}")
                reputation_score = 0.10
                break

    # Check standard TLDs vs high-risk TLDs
    if clean_dom.endswith(('.gov', '.edu', '.ac.uk')):
        signals.append("Authoritative institutional domain (.gov / .edu)")
        reputation_score = max(reputation_score, 0.90)
    elif clean_dom.endswith(('.top', '.xyz', '.buzz', '.biz', '.click', '.tk')):
        signals.append("High-risk or disposable top-level domain")
        reputation_score = min(reputation_score, 0.35)

    return {
        'domain': clean_dom,
        'publisher': matched_publisher or 'Independent / Unverified Domain',
        'is_recognized': matched_publisher is not None,
        'credibility_score': round(reputation_score, 2),
        'signals': signals
    }
