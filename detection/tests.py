import json
from django.test import TestCase, Client
from detection.models import DetectionLog
from detection.services.ai_reasoner import AIReasonerService


class DetectionAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_system_stats_endpoint(self):
        response = self.client.get('/api/system/stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('stats', data)
        stats = data['stats']
        for key in ['indexed_articles', 'user_articles', 'total_detections', 'db_size_mb', 'retention_policy_days']:
            self.assertIn(key, stats)

    def test_detect_api_missing_content(self):
        response = self.client.post(
            '/api/detect/',
            data=json.dumps({'content': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))

    def test_legacy_detect_endpoint_with_ai_reasoning(self):
        sample_text = "Officials report quarterly inflation slowed down according to central bank release."
        response = self.client.post(
            '/detect/',
            data=json.dumps({'content': sample_text}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('result', data)
        self.assertIn('confidence', data)
        self.assertIn('source', data)
        # Check newly integrated AI reasoning fields
        self.assertIn('why_real', data)
        self.assertIn('why_fake', data)
        self.assertIn('ai_summary', data)
        self.assertIn('ai_provider', data)
        self.assertIn('sentiment_analysis', data)
        self.assertIn('objectivity_pct', data)
        self.assertIn('journalistic_rigor', data)

    def test_detect_url_api_empty_url(self):
        response = self.client.post(
            '/api/detect/url/',
            data=json.dumps({'url': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))

    def test_detection_history_api(self):
        # Create sample detection logs
        DetectionLog.objects.create(
            query_text="Sample verified statement for audit testing.",
            input_type="text",
            result="Real News",
            confidence=92.0,
            source_info="FTS5 Index",
            response_time_ms=85.0
        )
        DetectionLog.objects.create(
            query_text="SHOCKING SECRET: Aliens discovered on moon!",
            input_type="text",
            result="Fake News",
            confidence=98.5,
            source_info="ML Ensemble",
            response_time_ms=110.0
        )

        # GET all history
        res = self.client.get('/api/detections/history/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(data.get('total'), 2)
        self.assertEqual(len(data.get('detections')), 2)

        # Filter by verdict
        filtered_res = self.client.get('/api/detections/history/?verdict=Fake')
        self.assertEqual(filtered_res.status_code, 200)
        f_data = filtered_res.json()
        self.assertEqual(f_data.get('total'), 1)
        self.assertIn("SHOCKING", f_data['detections'][0]['query_text'])

    def test_ai_reasoner_service_directly(self):
        analysis = AIReasonerService.analyze_and_explain(
            text="SHOCKING: Unbelievable conspiracy exposed by doctors! See why they don't want you to know!",
            verdict="Fake News",
            confidence=95.0,
            evidence={'article_db_match': False, 'indexed_corpus_match': True, 'matched_corpus_label': 'fake'},
            models={'predictions': {'logistic_regression': 0}},
            linguistic_signals={'sensational_terms': ['shocking', 'unbelievable'], 'has_clickbait_patterns': True, 'caps_ratio': 0.15, 'has_attribution': False}
        )
        self.assertIn('why_fake', analysis)
        self.assertGreater(len(analysis['why_fake']), 0)
        self.assertIn('ai_summary', analysis)
        self.assertIn('sentiment_analysis', analysis)
        self.assertIn('TruthLens', analysis['ai_provider'])
