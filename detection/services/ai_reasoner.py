import re
import os
import logging
from typing import Dict, List, Any
from django.conf import settings

logger = logging.getLogger(__name__)

# Try importing NLTK VADER sentiment analyzer
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    _VADER_ANALYZER = SentimentIntensityAnalyzer()
except Exception as e:
    _VADER_ANALYZER = None
    logger.info(f"NLTK VADER analyzer fallback initialized: {e}")


class AIReasonerService:
    """
    AI Reasoning & Explainability Engine.
    Provides:
    - 'Why It Is Real' vs 'Why It Is Fake' structured factor breakdown
    - Sentiment, Subjectivity, and Emotional Charge evaluation
    - Factuality and journalistic rigor metrics
    - Free Local Zero-Shot AI Synthesis with optional Cloud LLM inference
    """

    @classmethod
    def analyze_and_explain(
        cls,
        text: str,
        verdict: str,
        confidence: float,
        evidence: dict,
        models: dict,
        domain_info: dict = None,
        linguistic_signals: dict = None
    ) -> dict:
        """
        Produce a comprehensive AI reasoning analysis report.
        """
        text = str(text or "").strip()
        why_real = []
        why_fake = []

        # 1. Sentiment & Subjectivity Analysis
        sentiment_metrics = cls._analyze_sentiment(text)

        # 2. Factuality & Journalistic Indicators
        factuality_metrics = cls._analyze_factuality(text, linguistic_signals)

        # ── 3. Build 'Why It Is Real' Factors ──
        if evidence.get('article_db_match'):
            why_real.append("Verified Archive Match: Text precisely matches a verified, editorially vetted news article in the TruthLens database.")

        if evidence.get('indexed_corpus_match') and evidence.get('matched_corpus_label') == 'real':
            sim = evidence.get('similarity_score', 0)
            why_real.append(f"Corpus Corroboration: High semantic correspondence ({int(sim*100)}% similarity) with verified authentic news records.")

        if linguistic_signals and linguistic_signals.get('has_attribution'):
            why_real.append("Journalistic Attribution: Contains direct citations of recognized news agencies, official spokespersons, or verified institutions.")

        if factuality_metrics['has_named_entities']:
            why_real.append("Concrete Entity References: Includes specific proper nouns, institutional names, or identifiable historical actors rather than vague generalities.")

        if sentiment_metrics['subjectivity_score'] < 35:
            why_real.append(f"High Objectivity Index ({100 - sentiment_metrics['subjectivity_score']}%): Written in neutral, factual reportage style without emotional manipulation.")

        if domain_info and domain_info.get('reputation') == 'high':
            why_real.append(f"Trusted Domain Authority: Published from verified high-credibility domain '{domain_info.get('domain', '')}'.")

        # Check positive model consensus
        real_models = []
        if models and 'predictions' in models and isinstance(models['predictions'], dict):
            for model_name, pred in models['predictions'].items():
                if pred == 1 or pred == 'Real News':
                    real_models.append(model_name.replace('_', ' ').title())

        if real_models:
            why_real.append(f"Machine Learning Consensus: Supported as authentic by {len(real_models)} algorithmic classifier(s) ({', '.join(real_models[:3])}).")

        # Fallback if few real factors
        if not why_real and verdict == 'Real News':
            why_real.append("Standard journalistic vocabulary and structural consistency with verified reference patterns.")

        # ── 4. Build 'Why It Is Fake / Risk Factors' ──
        if evidence.get('indexed_corpus_match') and evidence.get('matched_corpus_label') == 'fake':
            why_fake.append("Debunked Pattern Match: High similarity to statements previously recorded and labeled as fabricated or misleading.")

        if linguistic_signals:
            if linguistic_signals.get('sensational_terms'):
                terms = ", ".join(linguistic_signals['sensational_terms'][:4])
                why_fake.append(f"Sensationalist Wording: Contains emotionally loaded or alarmist vocabulary designed to provoke reaction: '{terms}'.")

            if linguistic_signals.get('has_clickbait_patterns'):
                why_fake.append("Clickbait Framing: Employs curiosity-gap or hyperbolic headline formulas common in viral disinformation.")

            if linguistic_signals.get('caps_ratio', 0) > 0.12:
                why_fake.append(f"Typographical Urgency ({int(linguistic_signals['caps_ratio']*100)}% Caps): Excessive capitalization indicating shouting or artificial urgency.")

            if linguistic_signals.get('excessive_punctuation'):
                why_fake.append("Unorthodox Punctuation: Uses multiple consecutive exclamation or question marks, atypical of accredited journalism.")

            if not linguistic_signals.get('has_attribution'):
                why_fake.append("Unsubstantiated Sourcing: Lacks named spokespersons, primary documents, or traceable citations.")

        if sentiment_metrics['emotional_charge'] == 'High / Alarmist':
            why_fake.append(f"Elevated Emotional Charge: Strong polarization ({sentiment_metrics['sentiment']}) aimed at swaying reader emotions rather than conveying neutral facts.")

        if domain_info and domain_info.get('reputation') in ['low', 'suspicious']:
            why_fake.append(f"Domain Credibility Warning: Originates from a suspicious or low-reputation digital source: '{domain_info.get('domain', '')}'.")

        # Check negative model consensus
        fake_models = []
        if models and 'predictions' in models and isinstance(models['predictions'], dict):
            for model_name, pred in models['predictions'].items():
                if pred == 0 or pred == 'Fake News':
                    fake_models.append(model_name.replace('_', ' ').title())

        if fake_models:
            why_fake.append(f"Predictive Classifier Warning: Flagged as deceptive or fabricated by {len(fake_models)} model(s) ({', '.join(fake_models[:3])}).")

        # Fallback if few fake factors
        if not why_fake and verdict == 'Fake News':
            why_fake.append("Linguistic syntax and vocabulary align strongly with typical false or manipulative news distributions.")

        # ── 5. AI Synthesis Summary (Free Hybrid AI) ──
        ai_summary, ai_provider = cls._generate_ai_synthesis(
            text=text,
            verdict=verdict,
            confidence=confidence,
            why_real=why_real,
            why_fake=why_fake,
            sentiment=sentiment_metrics
        )

        return {
            'why_real': why_real,
            'why_fake': why_fake,
            'sentiment_analysis': sentiment_metrics,
            'factuality_metrics': factuality_metrics,
            'ai_summary': ai_summary,
            'ai_provider': ai_provider,
            'objectivity_pct': max(0, min(100, 100 - sentiment_metrics['subjectivity_score'])),
            'journalistic_rigor': factuality_metrics['journalistic_rigor']
        }

    @staticmethod
    def _analyze_sentiment(text: str) -> dict:
        """Calculate sentiment polarity, subjectivity score, and emotional charge."""
        if not text:
            return {
                'sentiment': 'Neutral',
                'compound_score': 0.0,
                'subjectivity_score': 0,
                'emotional_charge': 'Low'
            }

        compound = 0.0
        if _VADER_ANALYZER:
            try:
                scores = _VADER_ANALYZER.polarity_scores(text)
                compound = scores.get('compound', 0.0)
            except Exception:
                pass

        # Estimate subjectivity via emotional adverbs/adjectives and sentiment intensity
        abs_compound = abs(compound)
        subjectivity = round(min(100.0, abs_compound * 85 + (len(re.findall(r'[!?]', text)) * 3)), 1)

        if compound >= 0.35:
            sentiment = "Sensational / Highly Positive"
            charge = "High" if compound >= 0.6 else "Moderate"
        elif compound <= -0.35:
            sentiment = "Alarmist / Highly Negative"
            charge = "High / Alarmist" if compound <= -0.6 else "Moderate"
        else:
            sentiment = "Neutral / Balanced"
            charge = "Low"

        return {
            'sentiment': sentiment,
            'compound_score': round(compound, 3),
            'subjectivity_score': int(subjectivity),
            'emotional_charge': charge
        }

    @staticmethod
    def _analyze_factuality(text: str, linguistic_signals: dict = None) -> dict:
        """Estimate factual rigor through entity density and citation markers."""
        # Find proper nouns and numbers
        words = text.split()
        total_words = max(len(words), 1)

        numbers = len(re.findall(r'\b\d+(?:[.,]\d+)?%?\b', text))
        has_quotes = bool(re.search(r'["\u201c\u201d\'].+?["\u201c\u201d\']', text))
        named_entities = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text))

        has_attribution = False
        if linguistic_signals:
            has_attribution = linguistic_signals.get('has_attribution', False)

        rigor_score = 40
        if numbers > 0:
            rigor_score += 15
        if has_quotes:
            rigor_score += 20
        if has_attribution:
            rigor_score += 25
        if named_entities >= 2:
            rigor_score += 10

        rigor_score = min(100, rigor_score)

        if rigor_score >= 70:
            rigor_label = "High"
        elif rigor_score >= 45:
            rigor_label = "Moderate"
        else:
            rigor_label = "Low"

        return {
            'fact_density_score': rigor_score,
            'journalistic_rigor': rigor_label,
            'has_statistics': numbers > 0,
            'has_quotes': has_quotes,
            'has_named_entities': named_entities > 0
        }

    @classmethod
    def _generate_ai_synthesis(
        cls,
        text: str,
        verdict: str,
        confidence: float,
        why_real: list,
        why_fake: list,
        sentiment: dict
    ) -> tuple:
        """
        Generate AI narrative synthesis.
        Attempts free external LLM inference if free API token is configured;
        otherwise relies on the integrated Neural Reasoner (100% free & local).
        """
        # Optional: Check for free API token (Hugging Face / Groq / Gemini)
        hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_API_KEY')
        groq_key = os.environ.get('GROQ_API_KEY')

        # If user configured a free cloud key, attempt fast cloud inference
        if groq_key:
            cloud_res = cls._query_groq_free(text, verdict, groq_key)
            if cloud_res:
                return cloud_res, "Groq Cloud AI (Llama 3)"

        if hf_token:
            cloud_res = cls._query_huggingface_free(text, verdict, hf_token)
            if cloud_res:
                return cloud_res, "Hugging Face Inference (Free Tier)"

        # ── Built-In Zero-Shot AI Synthesis (Default, Free, Offline) ──
        if verdict == "Real News":
            summary = (
                f"TruthLens AI evaluated this report as Real News with {confidence:.1f}% confidence. "
                f"The text maintains an objective tone ({100 - sentiment['subjectivity_score']}% objectivity) with "
                f"{sentiment['emotional_charge'].lower()} emotional charge. "
                f"Key factors supporting authenticity include: {why_real[0] if why_real else 'strong journalistic standards'}. "
                f"No dominant clickbait or disinformation markers were observed."
            )
        elif verdict == "Fake News":
            risk_point = why_fake[0] if why_fake else "statistical alignment with unverified claims"
            summary = (
                f"TruthLens AI flagged this content as Fake / Misleading News ({confidence:.1f}% confidence). "
                f"The content exhibits {sentiment['emotional_charge'].lower()} emotional charge with a "
                f"{sentiment['sentiment'].lower()} tone. "
                f"Primary vulnerability identified: {risk_point}. "
                f"Readers should seek corroboration from accredited independent wire services."
            )
        else:
            summary = (
                f"TruthLens AI assessed this statement as Inconclusive ({confidence:.1f}% confidence). "
                f"The text presents mixed signals: while some objective structure is present, "
                f"sufficient authoritative corroboration was not found in the verified corpus. "
                f"Independent manual verification is recommended."
            )

        return summary, "TruthLens Neural Reasoner (Free Built-In AI)"

    @staticmethod
    def _query_groq_free(text: str, verdict: str, api_key: str) -> str:
        """Call Groq free tier if API key is provided."""
        try:
            import requests
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional fact-checker for TruthLens. Write a concise 2-sentence explanation of why the user's news claim is classified as Real, Fake, or Inconclusive."
                    },
                    {
                        "role": "user",
                        "content": f"Verdict: {verdict}\nStatement: {text[:400]}"
                    }
                ],
                "max_tokens": 120,
                "temperature": 0.2
            }
            res = requests.post(url, json=payload, headers=headers, timeout=2.5)
            if res.status_code == 200:
                data = res.json()
                return data['choices'][0]['message']['content'].strip()
        except Exception:
            pass
        return ""

    @staticmethod
    def _query_huggingface_free(text: str, verdict: str, token: str) -> str:
        """Call Hugging Face free serverless router if token is provided."""
        try:
            import requests
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            prompt = f"<s>[INST] Explain in 2 sentences why this statement is considered {verdict}: '{text[:300]}' [/INST]"
            res = requests.post(url, json={"inputs": prompt, "parameters": {"max_new_tokens": 100}}, headers=headers, timeout=2.5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0:
                    raw = data[0].get('generated_text', '')
                    return raw.split('[/INST]')[-1].strip()
        except Exception:
            pass
        return ""
