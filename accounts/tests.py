import json
from django.test import TestCase, Client
from django.contrib.auth.hashers import check_password, make_password
from accounts.models import Admin, Article


class AccountsAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Admin.objects.create(
            name="Test Officer",
            email="officer@example.com",
            password=make_password("Secret123!"),
            phone="1234567890",
            address="123 Test St",
            note="Test note"
        )
        # Create a legacy admin with plain-text password to verify auto-upgrade
        self.legacy_admin = Admin.objects.create(
            name="Legacy Officer",
            email="legacy@example.com",
            password="plain_password",
            phone="9876543210"
        )

    def test_registration_hashes_password(self):
        payload = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'StrongPassword999!',
            'phone': '5551234'
        }
        response = self.client.post(
            '/register/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        user = Admin.objects.get(email='newuser@example.com')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(check_password('StrongPassword999!', user.password))

    def test_login_success_and_session(self):
        payload = {'email': 'officer@example.com', 'password': 'Secret123!'}
        response = self.client.post(
            '/login-view/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('name'), 'Test Officer')
        self.assertEqual(self.client.session.get('admin_id'), self.admin.id)

    def test_login_invalid_password(self):
        payload = {'email': 'officer@example.com', 'password': 'WrongPassword'}
        response = self.client.post(
            '/login-view/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_legacy_password_auto_upgrade(self):
        # Legacy user starts with plaintext
        self.assertEqual(self.legacy_admin.password, 'plain_password')

        payload = {'email': 'legacy@example.com', 'password': 'plain_password'}
        response = self.client.post(
            '/login-view/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # After login, password must be hashed automatically
        self.legacy_admin.refresh_from_db()
        self.assertTrue(self.legacy_admin.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(check_password('plain_password', self.legacy_admin.password))


class ProfileAndArticleCrudTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = Admin.objects.create(
            name="Lead Editor",
            email="editor@example.com",
            password=make_password("editorPass123"),
            phone="5550001",
            address="Newsroom Floor 4",
            note="Lead news fact-checker"
        )
        # Authenticate session
        session = self.client.session
        session['admin_id'] = self.admin.id
        session.save()

    def test_profile_get_and_update(self):
        # GET profile
        get_res = self.client.get('/api/profile/')
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['email'], 'editor@example.com')

        # PUT/POST update
        update_res = self.client.post(
            '/api/profile/',
            data=json.dumps({
                'name': 'Lead Editor Updated',
                'phone': '5559999',
                'address': 'Newsroom HQ',
                'note': 'Senior Lead Editor'
            }),
            content_type='application/json'
        )
        self.assertEqual(update_res.status_code, 200)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.name, 'Lead Editor Updated')
        self.assertEqual(self.admin.phone, '5559999')

    def test_article_full_crud_cycle(self):
        # 1. Create Article
        create_res = self.client.post(
            '/api/articles/',
            data=json.dumps({
                'title': 'Automated Test Article',
                'username': 'Reuters',
                'description': 'Details regarding verification testing.',
                'rate': 4.2
            }),
            content_type='application/json'
        )
        self.assertEqual(create_res.status_code, 200)
        res_data = create_res.json()
        art_id = res_data.get('id') or res_data.get('article', {}).get('id')
        self.assertIsNotNone(art_id)

        # 2. Read Article
        detail_res = self.client.get(f'/api/articles/{art_id}/')
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()['title'], 'Automated Test Article')

        # 3. Update Article
        update_res = self.client.put(
            f'/api/articles/{art_id}/',
            data=json.dumps({
                'title': 'Automated Test Article (Updated)',
                'username': 'Reuters FactCheck',
                'description': 'Updated details.',
                'rate': 4.7
            }),
            content_type='application/json'
        )
        self.assertEqual(update_res.status_code, 200)

        # 4. Delete Article
        delete_res = self.client.delete(f'/api/articles/{art_id}/')
        self.assertEqual(delete_res.status_code, 200)
        self.assertFalse(Article.objects.filter(id=art_id).exists())
