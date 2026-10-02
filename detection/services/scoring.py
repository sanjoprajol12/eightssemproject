import logging

logger = logging.getLogger(__name__)

BM25_MIN = 0.75
SIMILARITY_MIN = 0.85
PROBABILITY_FLOOR = 0.03
PROBABILITY_CEILING = 0.97


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

        # 3. Corpus evidence: Exact match against verified dataset is definitive;
        # strong FTS hits provide decisive corroboration.
        corpus_adjustment = 0.0
        if corpus_match.get('matched'):
            match_type = corpus_match.get('match_type')
            label = corpus_match.get('label')
            matched_title = corpus_match.get('title', '')
            score = corpus_match.get('score', 0.5)

            if match_type == 'index_hash_exact':
                is_real_match = (label == 'real')
                verdict_label = 'Real News' if is_real_match else 'Fake News'
                evidence_points.append(f"Ground-truth dataset match found: '{matched_title[:80]}' [{label.upper()}]")
                return {
                    'result': verdict_label,
                    'confidence': 98.0,
                    'primary_source': f'Verified Ground-Truth Dataset ({corpus_match.get("source", "Indexed News")})',
                    'evidence_summary': evidence_points,
                    'is_inconclusive': False
                }

            bm25_score = corpus_match.get('bm25_score', 0.0)
            similarity_score = corpus_match.get('overlap_score', score)
            strong_corpus_match = (
                match_type == 'fts5_bm25'
                and bm25_score > BM25_MIN
                and similarity_score > SIMILARITY_MIN
            )
            if strong_corpus_match:
                evidence_points.append(f"Strong corpus corroboration: '{matched_title[:60]}' [{label.upper()}]")
                corpus_adjustment = -0.30 if label == 'real' else 0.30
            else:
                evidence_points.append(
                    f"Weak corpus match ignored for scoring: '{matched_title[:60]}' "
                    f"(BM25 {bm25_score:.2f}, overlap {similarity_score:.2f})."
                )

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

        # 5. ML Models Consensus. Stored probabilities represent P(real) for
        # the current models, so invert their mean to obtain P(fake).
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

        p_fake = 1.0 - avg_real_prob
        spread = (max(valid_probs) - min(valid_probs)) if valid_probs else 0.0
        p_fake += corpus_adjustment
        p_fake -= domain_weight
        p_fake = max(PROBABILITY_FLOOR, min(PROBABILITY_CEILING, p_fake))

        if not is_definitive:
            if spread > 0.5 or 0.35 < p_fake < 0.65:
                final_label = 'Inconclusive'
                confidence = round(max(p_fake, 1.0 - p_fake) * 100, 1)
                primary_source = 'Multi-Signal Analysis (Conflicting)'
                evidence_points.append(
                    f"Models disagree (probability spread {spread:.2f}); evidence is not decisive."
                )
            elif p_fake >= 0.65:
                final_label = 'Fake News'
                confidence = round(p_fake * 100, 1)
                primary_source = 'Ensemble ML Classifiers'
                evidence_points.append(f"ML models consensus: {int(p_fake * 100)}% probability of fabricated or unverified claims.")
            else:
                final_label = 'Real News'
                confidence = round((1.0 - p_fake) * 100, 1)
                primary_source = 'Ensemble ML Classifiers'
                evidence_points.append(f"ML models consensus: {int((1.0 - p_fake) * 100)}% probability of authentic reporting.")

        confidence = min(97.0, max(3.0, confidence))

        if not evidence_points:
            evidence_points.append("Evaluated across indexed corpus and trained linear models.")

        return {
            'result': final_label,
            'confidence': confidence,
            'primary_source': primary_source,
            'evidence_summary': evidence_points,
            'is_inconclusive': (final_label == 'Inconclusive')
        }
