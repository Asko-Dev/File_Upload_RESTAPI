from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from files.serializers import TagSerializer
from files.models import Tag

TAG_URL = reverse('files:tag-list')


def sample_tag(user, name='Invoices'):
    return Tag.objects.create(user=user, name=name)


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def tag_url_detail(tag_id):
    return reverse('files:tag-detail', args=[tag_id])


class PublicTagApi(TestCase):
    """Public tests for Tag"""

    def setUp(self):
        self.client = APIClient()

    def test_getting_tag_list(self):
        """Test not authorized won't see"""

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApi(TestCase):
    """Private tests for Tag"""

    def setUp(self):
        self.user = sample_user(
            name='TestName',
            email='tes@email.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Retrieve tags"""
        tag = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user, name='January Payments')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-id')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ones_tags(self):
        """Retrieve your tags"""
        user2 = sample_user(
            name='Second',
            email='second@email.com',
            password='testpass2'
        )
        tag1 = sample_tag(user=user2, name='Christmas List')
        tag2 = sample_tag(user=self.user)

        res = self.client.get(TAG_URL)

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag2.name)

    def test_create_tag_successful(self):
        """Test creating a tag"""
        payload = {'name': 'January Payments'}

        res = self.client.post(TAG_URL, payload)
        exists = Tag.objects.all().filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Invalid name"""
        payload = {'name': ' '}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_tag(self):
        """Updating a tag"""
        tag = sample_tag(user=self.user, name='Invoices')

        res = self.client.patch(tag_url_detail(tag.id), {'name': 'Shopping'})

        self.user.refresh_from_db()
        tag_updated = Tag.objects.filter(
            user=self.user,
            name='Shopping'
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(tag_updated)
