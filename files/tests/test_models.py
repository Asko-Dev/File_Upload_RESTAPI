from django.test import TestCase
from django.contrib.auth import get_user_model

from files import models


class ModelTests(TestCase):
    """Testing models to work"""

    def test_user_creation(self):
        """Testing creating a user"""
        email = 'Test@email.com'
        password = 'Testpass'

        user = get_user_model().objects.create_user(
            name='TestUser',
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Testing that email is normalized"""
        email = 'test@EMAIL.com'
        user = get_user_model().objects.create_user(
            name='TestUser',
            email=email,
            password='Testpass'
        )
        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email(self):
        """Testing invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                name='TestUser',
                email=None,
                password='Testpass'
                )

    def test_create_superuser(self):
        superuser = get_user_model().objects.create_superuser(
            name='Superuser',
            email='super@email.com',
            password='Testpass'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
