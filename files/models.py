import os
import hashlib
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


class UserManager(BaseUserManager):
    """Manager for the user model"""

    def create_user(self, name, email, password=None, **extra_fields):
        """Create a user"""
        if not email:
            raise ValueError('Email is required')
        user = self.model(
            name=name,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, email, password):
        """Create a superuser"""
        user = self.create_user(name, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=55, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('name',)

    def __str__(self):
        return self.email


class Tag(models.Model):
    """Tag to assign to file upload"""
    name = models.CharField(max_length=50, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    REQUIRED_FIELDS = ('name',)

    def __str__(self):
        return self.name


# Validation function for file upload
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[-1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            'Unsupported file format!\
 Supported: .pdf, .doc, .docx, .png, .jpg, .jpeg')


class FileUpload(models.Model):
    """File Upload Main Model"""
    PRIVATE = 'PRV'
    PUBLIC = 'PUB'

    PRV_PUB = [
        (PRIVATE, 'Private'),
        (PUBLIC, 'Public'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_uploaded = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=500)
    tag = models.ManyToManyField('Tag')
    visibility = models.CharField(
        max_length=3,
        choices=PRV_PUB,
        default=PRIVATE
    )
    file = models.FileField(
        blank=False,
        upload_to='user-files',
        validators=[validate_file_extension]
    )
    sha512_file_hash = models.CharField(max_length=200, default='Hash')

    REQUIRED_FIELDS = ('name', 'description', 'visibility', 'file',)

    def __str__(self):
        return (f'{self.user.name} - {self.name}')

    def save(self, *args, **kwargs):
        """Adding SHA-512 hash"""
        self.sha512_file_hash = self._hash_generator(self.file)
        super().save(*args, **kwargs)

    # hash generation for file upload
    def _hash_generator(self, file):
        sha512_file_hash = hashlib.sha512()
        for block in iter(lambda: file.read(4096), b""):
            sha512_file_hash.update(block)
        return sha512_file_hash.hexdigest()
