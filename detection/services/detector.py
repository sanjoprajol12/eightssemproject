import os
import time
import pickle
import joblib
import logging
from django.conf import settings

from detection.services.text_cleaner import clean_text
from detection.services.matcher import NewsMatcher
from detection.services.factcheck import query_google_fact_check
from detection.services.domain_analyzer import fetch_article_from_url, analyze_domain_credibility
from detection.services.explainability import ExplainabilityService
from detection.services.scoring import EnsembleScorer
from detection.services.ai_reasoner import AIReasonerService
from detection.models import DetectionLog

logger = logging.getLogger(__name__)

# Global model cache to ensure zero reload latency on requests
_LOADED_MODELS = {
    'initialized': False,
    'tfidf': None,
    'lr': None,
    'nb': None,
    'svm': None,
    'rf': None,
    'sgd': None,
    'flask_pipeline': None,
}


def _get_model_dir():
    """Resolve active ML models directory with fallback to legacy dir."""
    current_dir = getattr(settings, 'ML_MODELS_DIR', os.path.join(settings.BASE_DIR, 'ml_models', 'current'))
    if os.path.exists(current_dir):
        return current_dir
    legacy_dir = getattr(settings, 'ML_MODELS_LEGACY_DIR', os.path.join(settings.BASE_DIR, 'accounts', 'ml_models'))
    if os.path.exists(legacy_dir):
        return legacy_dir
    return current_dir


def load_ml_models():
    """
    Lazy load ML models once into memory.
    Keeps memory footprint bounded by using existing models without reloading large CSVs.
    """
    global _LOADED_MODELS
    if _LOADED_MODELS['initialized']:
        return _LOADED_MODELS

    model_dir = _get_model_dir()

    def _safe_load(filename):
        p = os.path.join(model_dir, filename)
        if os.path.exists(p):
            try:
                with open(p, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                try:
                    return joblib.load(p)
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
        return None

    # Load TF-IDF vectorizer
    _LOADED_MODELS['tfidf'] = _safe_load('tfidf.pkl')

    # Load individual classifiers
    _LOADED_MODELS['lr'] = _safe_load('lr_model.pkl')
    _LOADED_MODELS['nb'] = _safe_load('nb_model.pkl')
    _LOADED_MODELS['svm'] = _safe_load('svm_model.pkl')
    _LOADED_MODELS['rf'] = _safe_load('rf_model.pkl')
    _LOADED_MODELS['sgd'] = _safe_load('sgd_logistic.pkl')

    # Initialize HashingVectorizer for incremental SGD model
    from sklearn.feature_extraction.text import HashingVectorizer
    _LOADED_MODELS['hashing_vectorizer'] = HashingVectorizer(
        n_features=2**16,
        alternate_sign=False,
        norm='l2',
        ngram_range=(1, 2)
    )


    # Load Flask standalone pipeline (final_model.sav)
    flask_sav_path = os.path.join(settings.BASE_DIR, 'final_model.sav')
    if os.path.exists(flask_sav_path):
        try:
            with open(flask_sav_path, 'rb') as f:
                _LOADED_MODELS['flask_pipeline'] = pickle.load(f)
        except Exception as e:
            logger.warning(f"Could not load final_model.sav: {e}")

    _LOADED_MODELS['initialized'] = True
    logger.info("ML Models initialized successfully in memory.")
    return _LOADED_MODELS


class FakeNewsDetector:
    """
    Industry-standard Fake News Detection Pipeline:
    Input (Text/URL) -> Text Extraction -> Cleaning ->
    Evidence Matching (Article DB + FTS5 Index) ->
    Fact Check Verification -> ML Ensemble Inference ->
    Explainable AI (XAI) Analysis -> Credibility Report
    """

    @classmethod
    def detect(cls, content: str = "", url: str = "") -> dict:
        start_time = time.time()
        input_type = 'url' if url else 'text'
        target_text = (content or "").strip()
        domain_info = None
        extracted_title = ""

        # 1. URL Processing (if provided)
        if url:
            url_res = fetch_article_from_url(url)
            if not url_res.get('success'):
                return {
                    'success': False,
                    'error': url_res.get('error', 'Failed to fetch article from URL.'),
                    'status_code': 400
                }
            extracted_title = url_res.get('title', '')
            target_text = f"{extracted_title} {url_res.get('text', '')}".strip()
            domain_info = analyze_domain_credibility(
                url_res.get('domain', ''),
                is_https=url_res.get('is_https', True)
            )

        if not target_text:
            return {
                'success': False,
                'error': 'Please provide news text or a valid article URL to verify.',
                'status_code': 400
            }

        # 2. Text Cleaning
        cleaned = clean_text(target_text)

        # 3. Evidence Matcher: Verified Article DB & SQLite FTS5 Index
        article_match = NewsMatcher.match_article_table(target_text)
        if not article_match.get('matched'):
            # Also try matching against extracted title or first 100 characters
            article_match = NewsMatcher.match_article_table(target_text[:100])

        corpus_match = NewsMatcher.match_indexed_corpus(target_text)

        # 4. Optional Google Fact Check API
        factcheck_res = query_google_fact_check(extracted_title or target_text[:100])

        # 5. ML Models Inference
        models = load_ml_models()
        tfidf = models.get('tfidf')
        lr = models.get('lr')
        nb = models.get('nb')
        svm = models.get('svm')
        rf = models.get('rf')
        sgd = models.get('sgd')
        flask_pipe = models.get('flask_pipeline')

        model_predictions = {}
        model_probabilities = {}

        if tfidf is not None:
            try:
                vec = tfidf.transform([cleaned])

                if lr is not None:
                    pred = int(lr.predict(vec)[0])
                    model_predictions['logistic_regression'] = pred
                    if hasattr(lr, 'predict_proba'):
                        model_probabilities['logistic_regression'] = round(float(lr.predict_proba(vec)[0][1]), 3)

                if nb is not None:
                    pred = int(nb.predict(vec)[0])
                    model_predictions['naive_bayes'] = pred
                    if hasattr(nb, 'predict_proba'):
                        model_probabilities['naive_bayes'] = round(float(nb.predict_proba(vec)[0][1]), 3)

                if svm is not None:
                    pred = int(svm.predict(vec)[0])
                    model_predictions['linear_svm'] = pred

                if rf is not None:
                    pred = int(rf.predict(vec)[0])
                    model_predictions['random_forest'] = pred
                    if hasattr(rf, 'predict_proba'):
                        model_probabilities['random_forest'] = round(float(rf.predict_proba(vec)[0][1]), 3)
            except Exception as e:
                logger.warning(f"Error evaluating TF-IDF models: {e}")

        # Incremental SGD Classifier inference via HashingVectorizer
        h_vec = models.get('hashing_vectorizer')
        if sgd is not None and h_vec is not None:
            try:
                X_hash = h_vec.transform([cleaned])
                sgd_pred = int(sgd.predict(X_hash)[0])
                model_predictions['sgd_incremental'] = sgd_pred
                if hasattr(sgd, 'predict_proba'):
                    model_probabilities['sgd_incremental'] = round(float(sgd.predict_proba(X_hash)[0][1]), 3)
            except Exception as e:
                logger.warning(f"Error evaluating SGD incremental model: {e}")

        # Flask pipeline standalone inference (if available)

        if flask_pipe is not None:
            try:
                f_pred = flask_pipe.predict([target_text])[0]
                is_real_val = 1 if (f_pred is True or f_pred == 1 or str(f_pred).lower() == 'true') else 0
                model_predictions['flask_pipeline'] = is_real_val
                if hasattr(flask_pipe, 'predict_proba'):
                    f_prob = flask_pipe.predict_proba([target_text])[0]
                    # Find True index
                    classes = list(flask_pipe.classes_)
                    t_idx = classes.index(True) if True in classes else 1
                    model_probabilities['flask_pipeline'] = round(float(f_prob[t_idx]), 3)
            except Exception as e:
                logger.warning(f"Error evaluating flask_pipeline: {e}")

        # 6. Explainable AI Analysis
        explanation_data = ExplainabilityService.explain_prediction(
            target_text,
            tfidf_vectorizer=tfidf,
            lr_model=lr
        )

        # 7. Ensemble Scoring
        verdict = EnsembleScorer.calculate_verdict(
            article_match=article_match,
            corpus_match=corpus_match,
            model_predictions=model_predictions,
            model_probabilities=model_probabilities,
            factcheck_res=factcheck_res,
            domain_info=domain_info
        )

        # 8. AI Reasoning & Deep Explainability Analysis
        ai_analysis = AIReasonerService.analyze_and_explain(
            text=target_text,
            verdict=verdict['result'],
            confidence=verdict['confidence'],
            evidence={
                'article_db_match': article_match.get('matched', False),
                'indexed_corpus_match': corpus_match.get('matched', False),
                'matched_corpus_label': corpus_match.get('label') if corpus_match.get('matched') else None,
                'similarity_score': corpus_match.get('score', 0.0),
                'corpus_match_strength': corpus_match.get('match_strength', 'none'),
                'fact_check_match': factcheck_res.get('matched', False),
            },
            models={
                'predictions': model_predictions,
                'probabilities': model_probabilities
            },
            domain_info=domain_info,
            linguistic_signals=explanation_data.get('linguistic_metrics')
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # 9. Build structured Credibility Report
        report = {
            'success': True,
            'result': verdict['result'],
            'confidence': verdict['confidence'],
            'source': verdict['primary_source'],
            'why_real': ai_analysis['why_real'],
            'why_fake': ai_analysis['why_fake'],
            'sentiment_analysis': ai_analysis['sentiment_analysis'],
            'factuality_metrics': ai_analysis['factuality_metrics'],
            'bias_analysis': ai_analysis.get('bias_analysis', {}),
            'ai_summary': ai_analysis['ai_summary'],
            'ai_provider': ai_analysis['ai_provider'],
            'objectivity_pct': ai_analysis['objectivity_pct'],
            'journalistic_rigor': ai_analysis['journalistic_rigor'],
            'evidence': {
                'article_db_match': article_match.get('matched', False),
                'indexed_corpus_match': corpus_match.get('matched', False),
                'matched_corpus_label': corpus_match.get('label') if corpus_match.get('matched') else None,
                'similarity_score': corpus_match.get('score', 0.0),
                'bm25_score': corpus_match.get('bm25_score', 0.0),
                'overlap_score': corpus_match.get('overlap_score', 0.0),
                'corpus_match_strength': corpus_match.get('match_strength', 'none'),
                'fact_check_match': factcheck_res.get('matched', False),
                'evidence_points': verdict['evidence_summary']
            },
            'models': {
                'predictions': model_predictions,
                'probabilities': model_probabilities
            },
            'linguistic_signals': explanation_data['linguistic_metrics'],
            'model_signals': explanation_data['token_signals'],
            'explanation': [item['detail'] for item in explanation_data['explanation_items']],
            'domain_analysis': domain_info,
            'response_time_ms': elapsed_ms,
            'input_type': input_type,
            'article_title': extracted_title or target_text[:90]
        }

        # Determine if this detection needs human review (borderline confidence)
        needs_review = 40.0 <= verdict['confidence'] <= 65.0 or verdict['result'] == 'Inconclusive'

        # Extract bias data for persistence
        bias_info = ai_analysis.get('bias_analysis', {})
        bias_label = '; '.join(bias_info.get('bias_types', []))[:100]
        political_lean = bias_info.get('political_lean', 'neutral')


        # 9. Asynchronously/Safely Log Detection Request
        try:
            DetectionLog.objects.create(
                query_text=target_text[:1000],
                input_type=input_type,
                url=url if url else None,
                result=verdict['result'],
                confidence=verdict['confidence'],
                source_info=verdict['primary_source'],
                evidence=report['evidence'],
                model_predictions=report['models'],
                explanation=report['explanation'],
                response_time_ms=elapsed_ms,
                needs_review=needs_review,
                bias_label=bias_label,
                political_lean=political_lean,
            )
        except Exception as e:
            logger.warning(f"Failed to record DetectionLog: {e}")


        return report
