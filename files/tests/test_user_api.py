from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


USER_URL = reverse('files:user-create')
TOKEN_URL = reverse('files:user-token')
ME_URL = reverse('files:user-me')


def create_user(**params):
    """Sample user"""
    return get_user_model().objects.create_user(**params)


class PublicUserTestApis(TestCase):
    """Test Public Apis for a user"""

    def setUp(self):
        """What runs before tests"""
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a valid user through post request"""
        payload = {
            'name': 'TestUser',
            'email': 'test@email.com',
            'password': 'Testpass'
        }
        res = self.client.post(USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Testing FAIL post request if the same user already exists"""
        payload = {
            'name': 'TestUser',
            'email': 'email@email.com',
            'password': 'password'
        }
        user = create_user(**payload)

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testing not creating a password with a too short psw"""
        payload = {
            'name': 'TestUser',
            'email': 'email@email.com',
            'password': 'Hi'
        }
        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_retrieve_auth_token(self):
        """Test registered user retrieves the token"""
        payload = {
            'email': 'email@email.com',
            'password': 'Testpass'
        }
        user = create_user(name='Testname', **payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_not_retrieve_token(self):
        """Testing unregistered user can't get token"""
        payload = {
            'email': 'email@email.com',
            'password': 'Testpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_invalid_credentials(self):
        """Test auth doesn't go through with one correct"""
        payload = {
            'name': 'TestName',
            'email': 'email@email.com',
            'password': 'Testpass'
            }
        user = create_user(**payload)
        res = self.client.post(TOKEN_URL, {
            'email': 'email@email.com',
            'password': 'Testpass2'
            }
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_missing_field(self):
        """Test that doesn't go through with None"""
        res = self.client.post(TOKEN_URL, {
            'email': 'email@email.com',
            'password': ' '
            }
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_unauthorized_retrieve_user(self):
        """Test that unauthorized can't retrieve ME URL"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTestApis(TestCase):
    """Testing authorized actions"""

    def setUp(self):
        """Before every test"""
        self.user = create_user(
            name='TestName',
            email='test@email.com',
            password='Testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_success(self):
        """Test able to retrieve ME URL"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
            }
        )

    def test_post_me_not_allowed(self):
        """Test it throws an error when Me post"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        """Test PUT/PATCH on an authenticated user"""
        payload = {
            'name': 'ChangedName',
            'email': self.user.email,
            'password': self.user.password
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
        self.assertIn(res.data['name'], payload['name'])
