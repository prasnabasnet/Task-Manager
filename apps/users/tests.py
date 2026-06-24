from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse

User = get_user_model()


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role='TM'
        )
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.me_url = reverse('me')

    def test_register_success(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPass123',
            'role': 'PM'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_login_invalid_password(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Invalid email or password.')

    def test_logout_authenticated(self):
        login_data = {'email': 'test@example.com', 'password': 'testpass123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Successfully logged out.')
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_me_authenticated(self):
        login_data = {'email': 'test@example.com', 'password': 'testpass123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['role'], 'TM')

    def test_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 401)