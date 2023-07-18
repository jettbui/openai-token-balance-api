"""
Tests for the Balance API
"""
from balance.serializers import (
    BalanceSerializer,
)
from core.models import (
    Balance
)
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

BALANCE_URL = reverse('balance:balance-list')


def detail_url(user_id):
    """
    Helper function to return Balance detail URL.
    """
    return reverse('balance:balance-detail', args=[user_id])


def create_user(**params):
    """
    Helper function to create and return a User.
    """
    return get_user_model().objects.create_user(**params)


def get_user_balance(user):
    """
    Helper function to get a User's Balance.
    """
    return Balance.objects.filter(user=user).order_by('-id').first()


class PublicBalanceApiTests(TestCase):
    """Test API requests that do not require authentication."""

    def setUp(self):
        """Create client for testing."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(BALANCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBalanceApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        """Create client for testing."""
        self.user = create_user(
            email='test@example.com',
            password="testpass123",
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_balance(self):
        """Test retrieving authenticated User's Balance."""
        res = self.client.get(BALANCE_URL)
        balance = get_user_balance(self.user)
        serializer = BalanceSerializer(balance)

        self.assertIsNotNone(balance)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_other_balance_not_superuser(self):
        """Test retrieving another User's balance if not superuser."""
        user2 = create_user(
            email='test2@example.com',
            password="testpass456",
            name='Test Name 2',
        )
        url = detail_url(user2.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_balance_not_superuser(self):
        """Test updating another User's balance if not superuser."""
        user2 = create_user(
            email='test2@example.com',
            password="testpass456",
            name='Test Name 2',
        )
        payload = {
            'balance': 100,
        }
        url = detail_url(user2.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivilegedBalanceApiTests(TestCase):
    """Test API requests that require privileged authentication."""

    def setUp(self):
        """Create client for testing."""
        self.user = create_user(
            email='admin@example.com',
            password="testpass123",
            name='Test Admin',
            is_superuser=True,
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_other_balance(self):
        """Test retrieving another User's Balance as superuser."""
        user2 = create_user(
            email='test2@example.com',
            password="testpass456",
            name='Test Name 2',
        )
        url = detail_url(user2.id)
        res = self.client.get(url)
        balance = get_user_balance(user2)
        serializer = BalanceSerializer(balance)

        self.assertIsNotNone(balance)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_balance(self):
        """Test updating another User's Balance as superuser."""
        user2 = create_user(
            email='test2@example.com',
            password="testpass456",
            name='Test Name 2',
        )
        payload = {
            'balance': 125,
        }
        url = detail_url(user2.id)
        res = self.client.patch(url, payload)
        balance = get_user_balance(user2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(balance.balance, payload['balance'])

    def test_update_balance_user_returns_error(self):
        """Test changing the Balance user is not allowed."""
        user2 = create_user(
            email='test2@example.com',
            password="testpass456",
            name='Test Name 2',
        )
        payload = {
            'user': self.user.id,
        }
        url = detail_url(user2.id)
        res = self.client.patch(url, payload)
        balance = get_user_balance(user2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(balance.user, user2)
