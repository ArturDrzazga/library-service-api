from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

REGISTER_URL = "/api/users/register/"
TOKEN_URL = "/api/users/token/"
ME_URL = "/api/users/me/"


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        payload = {
            "email": "test@test.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", res.data)

    def test_register_user_email_already_exists(self):
        payload = {
            "email": "test@test.com",
            "password": "testpass123",
        }
        get_user_model().objects.create_user(**payload)
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_password_too_short(self):
        payload = {
            "email": "test@test.com",
            "password": "123",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token(self):
        get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )
        payload = {
            "email": "test@test.com",
            "password": "testpass123",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_obtain_token_wrong_password(self):
        get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )
        payload = {
            "email": "test@test.com",
            "password": "wrongpass",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_unauthenticated(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user)
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], user.email)

    def test_update_profile(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user)
        payload = {"first_name": "Updated"}
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["first_name"], "Updated")

    def test_update_password(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user)
        payload = {"password": "newpass123"}
        res = self.client.patch(ME_URL, payload)
        user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password("newpass123"))
