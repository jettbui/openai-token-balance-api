"""
Tests Models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Tests for Models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new User with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new Users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):
        """Test that creating a User without an email raises an error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass123')

    def test_create_superuser(self):
        """Test creating a new User as a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com', 'testpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_balance(self):
        """Test creating a new Balance for a User."""
        user = get_user_model().objects.create_user(
            'test@example.com', 'testpass123'
        )

        self.assertEqual(user.balance.user, user)
        self.assertEqual(user.balance.balance, 0)
