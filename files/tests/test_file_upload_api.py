import tempfile
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from PIL import Image

from files.serializers import FileUploadSerializer
from files.models import FileUpload

FILE_URL = reverse('files:fileupload-list')
PUBLIC_FILE_URL = reverse('files:public-list')


def sample_file(user, name='January', description='Hi', visibility='PUB',
                file='hello.pdf'):
    return FileUpload.objects.create(user=user,
                                     name=name,
                                     description=description,
                                     visibility=visibility,
                                     file=file)


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def file_upload_url_detail(fileupload_id):
    return reverse('files:fileupload-detail', args=[fileupload_id])


class PublicFileUploadApi(TestCase):
    """Public tests for FileUpload"""

    def setUp(self):
        self.client = APIClient()

    def test_getting_fileupload_list(self):
        """Test not authorized won't see"""

        res = self.client.get(FILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFileUploadApi(TestCase):
    """Private tests for FileUpload"""

    def setUp(self):
        self.user = sample_user(
            name='TestName',
            email='tes@email.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_public_file_uploads(self):
        """Retrieve public fileuploads"""
        user2 = sample_user(
            name='Second',
            email='second@email.com',
            password='testpass2'
        )

        file_upload1 = sample_file(user=self.user)
        file_upload2 = sample_file(user=user2, name='February')

        res = self.client.get(PUBLIC_FILE_URL)

        file_uploads = FileUpload.objects.all().order_by('-id')
        serializer = FileUploadSerializer(file_uploads, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(len(serializer.data), 2)

    def test_retrieve_public_file_uploads_private_hidden(self):
        """Retrieve public fileuploads with private hidden"""
        user2 = sample_user(
            name='Second',
            email='second@email.com',
            password='testpass2'
        )

        file_upload1 = sample_file(user=self.user, visibility='PRV')
        file_upload2 = sample_file(user=user2, name='February')

        res = self.client.get(PUBLIC_FILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_all_my_file_uploads(self):
        """Retrieve all my fileuploads"""
        file_upload1 = sample_file(user=self.user)
        file_upload2 = sample_file(user=self.user, name='February')

        res = self.client.get(FILE_URL)

        file_uploads = FileUpload.objects.all().order_by('-id')
        serializer = FileUploadSerializer(file_uploads, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(file_upload1.name, serializer.data[1]['name'])
        self.assertEqual(file_upload2.name, serializer.data[0]['name'])

    def test_retrieve_only_my_fileuploads(self):
        """Retrieve your fileuploads"""
        user2 = sample_user(
            name='Second',
            email='second@email.com',
            password='testpass2'
        )
        file_upload1 = sample_file(user=self.user)
        file_upload2 = sample_file(user=user2, name='February')

        res = self.client.get(FILE_URL)

        serializer1 = FileUploadSerializer(file_upload1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], file_upload1.name)

    def test_create_fileupload_successful(self):
        """Test creating a fileupload"""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            file = Image.new('RGB', (10, 10))
            file.save(ntf, format='JPEG')
            ntf.seek(0)

            payload = {
                'name': 'February',
                'description': 'Hello',
                'visbility': 'PRV',
                'file': ntf
            }
            # format='multipart'
            res = self.client.post(FILE_URL, payload)

            exists = FileUpload.objects.all().filter(
                user=self.user,
                name=payload['name']
            ).exists()

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            self.assertTrue(exists)

    def test_create_fileupload_invalid(self):
        """Invalid name"""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            file = Image.new('RGB', (10, 10))
            file.save(ntf, format='JPEG')
            ntf.seek(0)

            payload = {
                'name': '',
                'description': 'Hello',
                'visbility': 'PRV',
                'file': ntf
            }
            res = self.client.post(FILE_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_fileupload(self):
        """Updating a fileupload"""
        fileupload = sample_file(user=self.user)

        res = self.client.patch(
            file_upload_url_detail(fileupload.id),
            {'name': 'March'}
        )

        self.user.refresh_from_db()
        file_updated = FileUpload.objects.filter(
            user=self.user,
            name='March'
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(file_updated)
