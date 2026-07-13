from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class AuthAPITestCase(TestCase):
    """
    Tests for Registration, Login, Logout, and the 'Me' profile endpoint.
    """

    def setUp(self):
        self.client = APIClient()
        # Created with mandatory username
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            role="TM",
        )
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.me_url = reverse("me")

    def test_register_success(self):
        # Username is now required in the registration payload
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPass123",
            "role": "PM",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], "newuser@example.com")
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_ignores_role_override(self):
        # Verify that users cannot register themselves as ADMIN
        data = {
            "email": "attacker@example.com",
            "username": "attacker",
            "password": "AttackPass123",
            "role": "ADMIN",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="attacker@example.com")
        # Role should default to TM regardless of input
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
        # Obtain token
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Successfully logged out.")
        # Token should be deleted from DB
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_me_authenticated(self):
        login_data = {"email": "test@example.com", "password": "testpass123"}
        login_response = self.client.post(self.login_url, login_data, format="json")
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["role"], "TM")

    def test_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 401)


class UserViewSetTestCase(TestCase):
    """
    Tests for the User Admin ViewSet (Admin access to all users).
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="admin_user",
            password="adminpass123",
            role="ADMIN",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            username="member_user",
            password="memberpass123",
            role="TM",
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
        # Verify both users are present in the list
        emails = [u["email"] for u in response.data]
        self.assertIn("member@example.com", emails)
        self.assertIn("admin@example.com", emails)

    def test_list_users_as_non_admin_forbidden(self):
        self._auth_as(self.member_token)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_user_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.get(f"{self.list_url}{self.member.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "member_user")

    def test_partial_update_role_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.patch(
            f"{self.list_url}{self.member.id}/", {"role": "PM"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.role, "PM")

    def test_destroy_soft_deletes_as_admin(self):
        self._auth_as(self.admin_token)
        response = self.client.delete(f"{self.list_url}{self.member.id}/")
        self.assertEqual(response.status_code, 204)
        self.member.refresh_from_db()
        # Custom logic: destroy sets is_active to False
        self.assertFalse(self.member.is_active)
        self.assertTrue(User.objects.filter(id=self.member.id).exists())

    def test_destroy_as_non_admin_forbidden(self):
        self._auth_as(self.member_token)
        response = self.client.delete(f"{self.list_url}{self.admin.id}/")
        self.assertEqual(response.status_code, 403)
