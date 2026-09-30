import json
from django.test import TestCase, Client


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

    def test_legacy_detect_endpoint(self):
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

    def test_detect_url_api_empty_url(self):
        response = self.client.post(
            '/api/detect/url/',
            data=json.dumps({'url': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))
