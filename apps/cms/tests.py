import json
from django.test import TestCase, Client
from apps.cms.models import Enquiry
from apps.authentication.models import User
from rest_framework.authtoken.models import Token


class EnquiryAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin_tester',
            password='TestPassword123!',
            user_type='admin',
            is_staff=True
        )
        self.token = Token.objects.create(user=self.admin_user)

    def test_anonymous_user_can_submit_enquiry(self):
        payload = {
            'name': 'Sarah Connor',
            'email': 'sarah@resistance.org',
            'phone': '+1 555 0199',
            'subject': 'Fabricated AI Disinformation Report',
            'message': 'Submitting an investigation request regarding automated news synthesis.'
        }
        response = self.client.post(
            '/api/v1/cms/enquiries/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data.get('name'), 'Sarah Connor')
        self.assertEqual(data.get('email'), 'sarah@resistance.org')
        self.assertEqual(data.get('subject'), 'Fabricated AI Disinformation Report')
        self.assertFalse(data.get('mark_as_read'))

        # Verify persisted in database
        self.assertTrue(Enquiry.objects.filter(email='sarah@resistance.org').exists())

    def test_anonymous_user_cannot_list_enquiries(self):
        response = self.client.get('/api/v1/cms/enquiries/')
        self.assertEqual(response.status_code, 401)

    def test_authenticated_admin_can_list_enquiries(self):
        Enquiry.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Query',
            message='Need assistance.'
        )
        response = self.client.get(
            '/api/v1/cms/enquiries/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(data['count'], 1)
