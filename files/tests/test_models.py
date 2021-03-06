from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from files.models import Tag, FileUpload


class ModelTests(TestCase):
    """Testing models to work"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name='TestUser2',
            email='Test2@email.com',
            password='Testpass'
        )

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

    def test_create_tag(self):
        """Testing creating a tag"""
        tag = Tag.objects.create(user=self.user, name='Invoices')
        tags = Tag.objects.all()

        self.assertEqual(len(tags), 1)
        self.assertEqual(tags.get(name='Invoices'), tag)

    def test_create_file_upload(self):
        """Testing creating a file upload object"""
        FileUpload.objects.create(
            user=self.user,
            name='TestFile',
            description='Hello',
            visibility='PRV',
            file='hello.pdf'
            )

        exists = FileUpload.objects.filter(name='TestFile').exists()
        self.assertTrue(exists)

    def test_create_file_upload_invalid(self):
        """Testing the model is incorrect"""
        instance = FileUpload.objects.create(
            user=self.user,
            name='TestFile',
            description='',
            visibility='PRV',
            file='hello.pff'
            )

        with self.assertRaises(ValidationError):
            instance.full_clean()
