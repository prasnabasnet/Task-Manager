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
            email="test@example.com", password="testpass123", role="TM"
        )
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.me_url = reverse("me")

    def test_register_success(self):
        data = {"email": "newuser@example.com", "password": "NewPass123", "role": "PM"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], "newuser@example.com")
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_ignores_role_override(self):
        data = {
            "email": "attacker@example.com",
            "password": "AttackPass123",
            "role": "ADMIN",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="attacker@example.com")
        self.assertEqual(user.role, "TM")

    def test_login_success(self):
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_login_invalid_password(self):
        data = {"email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"], "Invalid email or password.")

    def test_logout_authenticated(self):
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Successfully logged out.")
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_me_authenticated(self):
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["role"], "TM")

    def test_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 401)


class UserViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com", password="adminpass123", role="ADMIN"
        )
        self.member = User.objects.create_user(
            email="member@example.com", password="memberpass123", role="TM"
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.member_token = Token.objects.create(user=self.member)
        self.list_url = "/api/users/"

    def _auth_as(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list_users_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        emails = [u["email"] for u in response.data]
        self.assertIn("member@example.com", emails)

    def test_list_users_as_non_admin_forbidden(self):
        self._auth_as(self.member_token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_list_users_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_retrieve_user_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.get(f"{self.list_url}{self.member.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "member@example.com")

    def test_partial_update_role_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.patch(
            f"{self.list_url}{self.member.id}/", {"role": "PM"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.role, "PM")

    def test_create_disabled(self):
        self._auth_as(self.admin_token)
        response = self.client.post(
            self.list_url,
            {"email": "new@example.com", "password": "x", "role": "TM"},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

    def test_full_update_disabled(self):
        self._auth_as(self.admin_token)
        response = self.client.put(
            f"{self.list_url}{self.member.id}/",
            {"email": "member@example.com", "role": "PM"},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

    def test_destroy_soft_deletes_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.delete(f"{self.list_url}{self.member.id}/")
        self.assertEqual(response.status_code, 204)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)
        self.assertTrue(User.objects.filter(id=self.member.id).exists())

    def test_destroy_as_non_admin_forbidden(self):
        self._auth_as(self.member_token)
        response = self.client.delete(f"{self.list_url}{self.admin.id}/")
        self.assertEqual(response.status_code, 403)
