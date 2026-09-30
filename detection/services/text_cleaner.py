import re
import unicodedata
try:
    import emoji
except ImportError:
    emoji = None


SENSATIONAL_WORDS = {
    'shocking', 'unbelievable', 'bombshell', 'exposed', 'conspiracy', 'secret',
    'hidden', 'disaster', 'miracle', 'terrifying', 'horrific', 'outrage', 'insane',
    'mind-blowing', 'jaw-dropping', 'catastrophe', 'panic', 'apocalypse', 'scandal',
    'treason', 'cover-up', 'hoax', 'bizarre', 'nightmare', 'furious', 'explosive'
}

CLICKBAIT_PATTERNS = [
    r'\b(you won\'?t believe|will blow your mind|what happens next|the reason why|see why|this is why)\b',
    r'\b(\d+\s+(reasons|things|facts|ways|secrets|photos))\b',
    r'\b(they don\'?t want you to know|doctors hate|secret trick|miracle cure)\b',
]

ATTRIBUTION_PATTERNS = [
    r'\b(according to|reported by|stated by|confirmed by|sources say|spokesperson said|official said|in a statement)\b',
    r'\b(reuters|associated press|ap|bbc|afp|bloomberg)\b'
]


def clean_text(text: str) -> str:
    """
    Standard text cleaner:
    - Removes URLs
    - Normalizes unicode
    - Removes emojis
    - Removes special symbols
    - Lowercases and collapses multiple whitespaces
    """
    if not text:
        return ""
    text = str(text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text, flags=re.MULTILINE)
    # Remove mentions and hashtags
    text = re.sub(r'[@#]\w+', ' ', text)
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    # Remove emoji
    if emoji:
        text = emoji.replace_emoji(text, replace=' ')
    # Keep alphanumeric and basic spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Lowercase and whitespace normalization
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def analyze_linguistic_signals(raw_text: str) -> dict:
    """
    Extract linguistic signals for explainable AI:
    - Sensational language density
    - Clickbait pattern matches
    - Caps ratio
    - Excessive punctuation
    - Attribution markers
    """
    if not raw_text:
        return {
            'sensational_terms': [],
            'has_clickbait_patterns': False,
            'caps_ratio': 0.0,
            'excessive_punctuation': False,
            'has_attribution': False,
        }

    raw = str(raw_text)
    words = re.findall(r'\b[a-zA-Z]+\b', raw)
    lower_words = [w.lower() for w in words]

    # Sensational words found
    found_sensational = sorted(list(set(lower_words).intersection(SENSATIONAL_WORDS)))

    # Clickbait phrases
    has_clickbait = any(bool(re.search(pat, raw, re.IGNORECASE)) for pat in CLICKBAIT_PATTERNS)

    # Caps ratio (percentage of uppercase letters)
    letters = [c for c in raw if c.isalpha()]
    caps = [c for c in letters if c.isupper()]
    caps_ratio = round(len(caps) / max(len(letters), 1), 3)

    # Excessive punctuation (e.g. !!!, ???, !?!)
    excessive_punct = bool(re.search(r'[!?]{2,}', raw))

    # Attribution markers
    has_attribution = any(bool(re.search(pat, raw, re.IGNORECASE)) for pat in ATTRIBUTION_PATTERNS)

    return {
        'sensational_terms': found_sensational,
        'has_clickbait_patterns': has_clickbait,
        'caps_ratio': caps_ratio,
        'excessive_punctuation': excessive_punct,
        'has_attribution': has_attribution,
    }
