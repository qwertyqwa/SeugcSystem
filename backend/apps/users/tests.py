from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthApiTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.me_url = reverse("me")

    def test_register_client_success(self):
        payload = {
            "username": "client_one",
            "email": "client1@example.com",
            "password": "StrongPass123",
            "role": "client",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["role"], "client")
        self.assertTrue(User.objects.filter(username="client_one").exists())

    def test_register_manager_requires_admin(self):
        payload = {
            "username": "manager_bad",
            "email": "manager_bad@example.com",
            "password": "StrongPass123",
            "role": "manager",
        }

        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("Only admin users can create manager accounts.", str(response.data))

    def test_staff_user_can_register_manager(self):
        staff_user = User.objects.create_user(
            username="admin_user",
            email="admin@example.com",
            password="StrongPass123",
            role="manager",
            is_staff=True,
        )
        self.client.force_authenticate(staff_user)

        payload = {
            "username": "manager_ok",
            "email": "manager_ok@example.com",
            "password": "StrongPass123",
            "role": "manager",
        }
        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["role"], "manager")

    def test_login_returns_tokens_and_user(self):
        User.objects.create_user(
            username="login_user",
            email="login@example.com",
            password="StrongPass123",
            role="client",
        )

        response = self.client.post(
            self.login_url,
            {"username": "login_user", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["username"], "login_user")

    def test_me_requires_auth(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user_data(self):
        user = User.objects.create_user(
            username="me_user",
            email="me@example.com",
            password="StrongPass123",
            role="client",
        )
        self.client.force_authenticate(user)

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["id"], user.id)
        self.assertEqual(response.data["data"]["role"], "client")
