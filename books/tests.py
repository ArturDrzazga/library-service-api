from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Book

BOOKS_URL = "/api/books/"


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "SOFT",
        "inventory": 5,
        "daily_fee": 1.50,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class BookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="testpass123",
        )
        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="testpass123",
        )

    def test_list_books(self):
        sample_book()
        sample_book(title="Second Book")
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_book(self):
        book = sample_book()
        res = self.client.get(f"{BOOKS_URL}{book.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["title"], book.title)

    def test_create_book_admin(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "HARD",
            "inventory": 3,
            "daily_fee": 2.00,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

    def test_update_book_admin(self):
        book = sample_book()
        self.client.force_authenticate(self.admin)
        payload = {"title": "Updated Title"}
        res = self.client.patch(f"{BOOKS_URL}{book.id}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, "Updated Title")

    def test_delete_book_admin(self):
        book = sample_book()
        self.client.force_authenticate(self.admin)
        res = self.client.delete(f"{BOOKS_URL}{book.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_list_books_unauthenticated(self):
        sample_book()
        res = self.client.get(BOOKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_unauthenticated(self):
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 1.50,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_regular_user(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 1.50,
        }
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_regular_user(self):
        book = sample_book()
        self.client.force_authenticate(self.user)
        payload = {"title": "Updated Title"}
        res = self.client.patch(f"{BOOKS_URL}{book.id}/", payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_regular_user(self):
        book = sample_book()
        self.client.force_authenticate(self.user)
        res = self.client.delete(f"{BOOKS_URL}{book.id}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
