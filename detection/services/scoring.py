import logging

logger = logging.getLogger(__name__)


class EnsembleScorer:
    """
    Ensemble layer combining database evidence, full-text search matching,
    multiple ML classifier probabilities, and domain credibility signals.
    """

    @staticmethod
    def calculate_verdict(
        article_match: dict,
        corpus_match: dict,
        model_predictions: dict,
        model_probabilities: dict,
        factcheck_res: dict,
        domain_info: dict = None
    ) -> dict:
        """
        Synthesize multi-modal evidence into a final credibility verdict and confidence.
        """
        evidence_points = []
        is_definitive = False
        final_label = 'Inconclusive'
        confidence = 50.0
        primary_source = 'Hybrid Ensemble Analysis'

        # 1. Exact match in Verified Article Table (Highest authority)
        if article_match.get('matched'):
            match_type = article_match.get('match_type')
            if match_type == 'article_table_exact':
                evidence_points.append("Exact match found in verified Article Database.")
                return {
                    'result': 'Real News',
                    'confidence': 98.0,
                    'primary_source': 'Verified Article Database',
                    'evidence_summary': evidence_points,
                    'is_inconclusive': False
                }
            elif match_type == 'article_table_partial':
                evidence_points.append(f"High-confidence match with verified article: '{article_match.get('title')}'")
                final_label = 'Real News'
                confidence = 88.0
                primary_source = 'Article Database (Partial Match)'
                is_definitive = True

        # 2. Fact Check Match from External Authority
        if factcheck_res and factcheck_res.get('matched'):
            claims = factcheck_res.get('claims', [])
            if claims:
                top_claim = claims[0]
                reviews = top_claim.get('reviews', [])
                rating_str = reviews[0].get('rating', '') if reviews else ''
                publisher = reviews[0].get('publisher', 'Independent Fact-Checker') if reviews else ''

                if any(w in rating_str.lower() for w in ['false', 'fake', 'pants on fire', 'incorrect', 'hoax', 'misleading']):
                    evidence_points.append(f"External Fact-Check ({publisher}): Flagged as '{rating_str}'")
                    return {
                        'result': 'Fake News',
                        'confidence': 95.0,
                        'primary_source': f'Google Fact Check ({publisher})',
                        'evidence_summary': evidence_points,
                        'is_inconclusive': False
                    }
                elif any(w in rating_str.lower() for w in ['true', 'correct', 'accurate']):
                    evidence_points.append(f"External Fact-Check ({publisher}): Verified as '{rating_str}'")
                    return {
                        'result': 'Real News',
                        'confidence': 95.0,
                        'primary_source': f'Google Fact Check ({publisher})',
                        'evidence_summary': evidence_points,
                        'is_inconclusive': False
                    }

        # 3. Exact Hash or Strong FTS Match against Indexed Corpus
        if corpus_match.get('matched'):
            match_type = corpus_match.get('match_type')
            label = corpus_match.get('label')
            matched_title = corpus_match.get('title', '')
            score = corpus_match.get('score', 0.5)

            if match_type == 'index_hash_exact':
                if label == 'real':
                    evidence_points.append(f"Exact hash match in verified news corpus: '{matched_title[:60]}'")
                    return {
                        'result': 'Real News',
                        'confidence': 96.0,
                        'primary_source': 'Indexed News Corpus (Exact Hash)',
                        'evidence_summary': evidence_points,
                        'is_inconclusive': False
                    }
                else:
                    evidence_points.append(f"Exact hash match in verified fake news database: '{matched_title[:60]}'")
                    return {
                        'result': 'Fake News',
                        'confidence': 96.0,
                        'primary_source': 'Indexed Fake News Archive (Exact Hash)',
                        'evidence_summary': evidence_points,
                        'is_inconclusive': False
                    }
            elif match_type == 'fts5_bm25' and score >= 0.75:
                if label == 'real':
                    evidence_points.append(f"High-ranking match in indexed real news corpus: '{matched_title[:60]}'")
                    final_label = 'Real News'
                    confidence = max(confidence, round(score * 100, 1))
                    primary_source = 'FTS5 Indexed Corpus Match'
                    is_definitive = True
                elif label == 'fake':
                    evidence_points.append(f"High-ranking match in indexed fake news corpus: '{matched_title[:60]}'")
                    final_label = 'Fake News'
                    confidence = max(confidence, round(score * 100, 1))
                    primary_source = 'FTS5 Fake Corpus Match'
                    is_definitive = True

        # 4. Domain Reputation Evidence (if URL input)
        domain_weight = 0.0
        if domain_info:
            cred = domain_info.get('credibility_score', 0.5)
            if cred >= 0.90:
                evidence_points.append(f"Published on recognized reputable domain: {domain_info.get('publisher')}")
                domain_weight = 0.25
            elif cred <= 0.20:
                evidence_points.append(f"Published on known satirical or dubious domain: {domain_info.get('publisher')}")
                return {
                    'result': 'Fake News',
                    'confidence': 92.0,
                    'primary_source': f"Known Satirical/Dubious Publisher ({domain_info.get('domain')})",
                    'evidence_summary': evidence_points,
                    'is_inconclusive': False
                }

        # 5. ML Models Consensus
        # Valid models: logistic_regression, naive_bayes, linear_svm, sgd_incremental, flask_pipeline
        valid_probs = []
        model_votes = []

        for name, prob in model_probabilities.items():
            if prob is not None:
                valid_probs.append(prob)

        for name, pred in model_predictions.items():
            if pred is not None:
                model_votes.append(pred)

        if valid_probs:
            avg_real_prob = sum(valid_probs) / len(valid_probs)
        elif model_votes:
            avg_real_prob = sum(model_votes) / len(model_votes)
        else:
            avg_real_prob = 0.50

        # Adjust with domain credibility if present
        adjusted_real_prob = min(0.99, max(0.01, avg_real_prob + domain_weight))

        if not is_definitive:
            if adjusted_real_prob >= 0.65:
                final_label = 'Real News'
                confidence = round(adjusted_real_prob * 100, 1)
                primary_source = 'Ensemble ML Classifiers'
                evidence_points.append(f"ML models consensus: {int(adjusted_real_prob * 100)}% probability of authentic reporting.")
            elif adjusted_real_prob <= 0.38:
                final_label = 'Fake News'
                fake_prob = 1.0 - adjusted_real_prob
                confidence = round(fake_prob * 100, 1)
                primary_source = 'Ensemble ML Classifiers'
                evidence_points.append(f"ML models consensus: {int(fake_prob * 100)}% probability of fabricated or unverified claims.")
            else:
                final_label = 'Inconclusive'
                confidence = round(max(adjusted_real_prob, 1.0 - adjusted_real_prob) * 100, 1)
                primary_source = 'Multi-Signal Analysis (Borderline)'
                evidence_points.append("Conflicting or insufficient evidence between models and indexing.")

        if not evidence_points:
            evidence_points.append("Evaluated across indexed corpus and trained linear models.")

        return {
            'result': final_label,
            'confidence': confidence,
            'primary_source': primary_source,
            'evidence_summary': evidence_points,
            'is_inconclusive': (final_label == 'Inconclusive')
        }
