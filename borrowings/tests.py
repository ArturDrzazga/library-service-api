from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing

BORROWINGS_URL = "/api/borrowings/"

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

def sample_borrowing(user, book, **params):
    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=7),
        "book": book,
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class BorrowingApiTests(TestCase):
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
        self.user2 = get_user_model().objects.create_user(
            email="user2@test.com",
            password="testpass123",
        )
        self.book = sample_book()

    def test_list_borrowings_unauthenticated(self):
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings_authenticated(self):
        sample_borrowing(self.user, self.book)
        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_user_sees_only_own_borrowings(self):
        sample_borrowing(self.user, self.book)
        sample_borrowing(self.user2, self.book)
        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(len(res.data), 1)

    def test_admin_sees_all_borrowings(self):
        sample_borrowing(self.user, self.book)
        sample_borrowing(self.user2, self.book)
        self.client.force_authenticate(self.admin)
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(len(res.data), 2)

    def test_filter_active_borrowings(self):
        sample_borrowing(self.user, self.book)
        sample_borrowing(self.user, self.book, actual_return_date=date.today())
        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWINGS_URL, {"is_active": "true"})
        self.assertEqual(len(res.data), 1)

    def test_filter_inactive_borrowings(self):
        sample_borrowing(self.user, self.book)
        sample_borrowing(self.user, self.book, actual_return_date=date.today())
        self.client.force_authenticate(self.user)
        res = self.client.get(BORROWINGS_URL, {"is_active": "false"})
        self.assertEqual(len(res.data), 1)

    def test_admin_filter_by_user_id(self):
        sample_borrowing(self.user, self.book)
        sample_borrowing(self.user2, self.book)
        self.client.force_authenticate(self.admin)
        res = self.client.get(BORROWINGS_URL, {"user_id": self.user.id})
        self.assertEqual(len(res.data), 1)

    def test_create_borrowing(self):
        self.client.force_authenticate(self.user)
        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        res = self.client.post(BORROWINGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)

    def test_create_borrowing_no_inventory(self):
        self.book.inventory = 0
        self.book.save()
        self.client.force_authenticate(self.user)
        payload = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        res = self.client.post(BORROWINGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self):
        borrowing = sample_borrowing(self.user, self.book)
        self.client.force_authenticate(self.user)
        res = self.client.post(f"{BORROWINGS_URL}{borrowing.id}/return/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertEqual(borrowing.actual_return_date, date.today())
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_borrowing_twice(self):
        borrowing = sample_borrowing(
            self.user, self.book, actual_return_date=date.today()
        )
        self.client.force_authenticate(self.user)
        res = self.client.post(f"{BORROWINGS_URL}{borrowing.id}/return/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
