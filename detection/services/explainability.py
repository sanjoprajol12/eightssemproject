import logging
from detection.services.text_cleaner import analyze_linguistic_signals

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """
    Explainable AI (XAI) service providing transparent model signals:
    - Identifies informative token weights from the linear classifier.
    - Highlights sensational and clickbait phrasing.
    - Evaluates attribution and journalistic rigor markers.
    """

    @staticmethod
    def explain_prediction(text: str, tfidf_vectorizer=None, lr_model=None) -> dict:
        """
        Produce a structured explanation with model feature weights and linguistic cues.
        """
        linguistics = analyze_linguistic_signals(text)
        explanation_items = []
        token_signals = []

        # 1. Linguistic and Stylistic Signals
        if linguistics['sensational_terms']:
            terms_preview = ", ".join(linguistics['sensational_terms'][:5])
            explanation_items.append({
                'category': 'Language Tone',
                'signal': 'Elevated Sensational Vocabulary',
                'impact': 'negative',
                'detail': f"Detected emotionally charged wording: {terms_preview}"
            })

        if linguistics['has_clickbait_patterns']:
            explanation_items.append({
                'category': 'Headline Pattern',
                'signal': 'Clickbait Framing Detected',
                'impact': 'negative',
                'detail': 'Text contains curiosity hooks or sensational phrasing typical of clickbait.'
            })

        if linguistics['excessive_punctuation']:
            explanation_items.append({
                'category': 'Typography',
                'signal': 'Excessive Punctuation',
                'impact': 'negative',
                'detail': 'Multiple consecutive exclamation or question marks detected.'
            })

        if linguistics['caps_ratio'] > 0.15:
            explanation_items.append({
                'category': 'Typography',
                'signal': 'High Capitalization Ratio',
                'impact': 'negative',
                'detail': f"{int(linguistics['caps_ratio'] * 100)}% of characters are uppercase, indicating shouting or urgency framing."
            })

        if linguistics['has_attribution']:
            explanation_items.append({
                'category': 'Sourcing',
                'signal': 'Journalistic Attribution Markers',
                'impact': 'positive',
                'detail': 'Direct references to news agencies, official statements, or named sources found.'
            })
        else:
            explanation_items.append({
                'category': 'Sourcing',
                'signal': 'Unattributed Claims',
                'impact': 'neutral',
                'detail': 'No explicit citations, named spokespersons, or official sources detected.'
            })

        # 2. Linear Classifier Feature Importance (if vectorizer and model provided)
        if tfidf_vectorizer is not None and lr_model is not None and hasattr(lr_model, 'coef_'):
            try:
                feature_names = tfidf_vectorizer.get_feature_names_out()
                coefs = lr_model.coef_[0]
                vec = tfidf_vectorizer.transform([text])

                # Get non-zero indices for the given text
                nonzero_indices = vec.nonzero()[1]
                word_weights = []

                for idx in nonzero_indices:
                    word = feature_names[idx]
                    tfidf_val = vec[0, idx]
                    weight = float(coefs[idx] * tfidf_val)
                    word_weights.append((word, weight))

                # Sort by weight: positive weight -> favors Real; negative weight -> favors Fake
                word_weights.sort(key=lambda x: x[1])

                top_fake_tokens = [w for w, score in word_weights[:4] if score < -0.05]
                top_real_tokens = [w for w, score in reversed(word_weights[-4:]) if score > 0.05]

                for w in top_fake_tokens:
                    token_signals.append({
                        'token': w,
                        'tendency': 'Fake News Association',
                        'weight': round(float(next(s for word, s in word_weights if word == w)), 3)
                    })

                for w in top_real_tokens:
                    token_signals.append({
                        'token': w,
                        'tendency': 'Real News Association',
                        'weight': round(float(next(s for word, s in word_weights if word == w)), 3)
                    })

                if top_fake_tokens:
                    explanation_items.append({
                        'category': 'Model Term Association',
                        'signal': 'Corpus Patterns (Sensational/Fabricated bias)',
                        'impact': 'negative',
                        'detail': f"Tokens statistically correlated with unverified content: {', '.join(top_fake_tokens)}"
                    })

                if top_real_tokens:
                    explanation_items.append({
                        'category': 'Model Term Association',
                        'signal': 'Corpus Patterns (Factual/Journalistic bias)',
                        'impact': 'positive',
                        'detail': f"Tokens statistically correlated with verified reporting: {', '.join(top_real_tokens)}"
                    })
            except Exception as e:
                logger.warning(f"Feature importance extraction error: {e}")

        return {
            'explanation_items': explanation_items,
            'token_signals': token_signals,
            'linguistic_metrics': {
                'caps_ratio_pct': int(linguistics['caps_ratio'] * 100),
                'sensational_word_count': len(linguistics['sensational_terms']),
                'has_attribution': linguistics['has_attribution']
            }
        }
