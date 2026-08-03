from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class SilkIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User",
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="user@example.com",
            password="password123",
            first_name="Regular",
            last_name="User",
        )

    def test_silk_unauthenticated_redirects_to_login(self):
        """Unauthenticated requests to /silk/ should redirect to /djadmin/login/?next=/silk/"""
        response = self.client.get("/silk/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/djadmin/login/", response.url)

    def test_admin_login_page_renders(self):
        """Admin login page configured as LOGIN_URL should return 200 OK."""
        response = self.client.get("/djadmin/login/")
        self.assertEqual(response.status_code, 200)

    def test_silk_authenticated_superuser_access(self):
        """Authenticated staff/superuser can access the Silk dashboard."""
        self.client.login(email="admin@example.com", password="password123")
        response = self.client.get("/silk/")
        self.assertEqual(response.status_code, 200)
