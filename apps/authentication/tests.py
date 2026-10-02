import json
from django.test import TestCase, Client
from django.core.management import call_command
from apps.authentication.models import User
from rest_framework.authtoken.models import Token


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_seed_admin_command(self):
        call_command('seed_admin')
        self.assertTrue(User.objects.filter(email='pashupati@python.py').exists())
        user = User.objects.get(email='pashupati@python.py')
        self.assertTrue(user.check_password('Forgot911!'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_login_api_success(self):
        User.objects.create_user(
            email='reporter@test.com',
            username='reporter',
            password='ValidPassword99!',
            user_type='admin',
            is_staff=True
        )
        response = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({
                'login': 'reporter@test.com',
                'password': 'ValidPassword99!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['email'], 'reporter@test.com')

    def test_login_api_invalid_credentials(self):
        response = self.client.post(
            '/api/v1/auth/login/',
            data=json.dumps({
                'login': 'nonexistent@test.com',
                'password': 'WrongPassword!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
