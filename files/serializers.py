from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from .models import User, Tag, FileUpload


class UserSerializer(serializers.ModelSerializer):
    """Serializes User"""

    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'password')
        extra_kwargs = {'password': {
            'write_only': True,
            'min_length': 5,
            'style': {'input_type': 'password'}
            }
        }

    def create(self, validated_data):
        """Create and return new user"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user data"""
        password = validated_data.pop('password')
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Validates and authenticates a user"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=True
    )

    def validate(self, attrs):
        """Validates and authenticates the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag Model"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
        extra_kwargs = {'name': {'min_length': 4}}


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for the main File Upload Model"""
    tag = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = FileUpload
        fields = ('id', 'user' 'name', 'date_uploaded', 'file', 'tag',
                  'visibility', 'description')
        read_only_fields = ('id', 'date_uploaded',)


class FileUploadDetailSerializer(FileUploadSerializer):
    """Detail view for the file upload"""
    tag = TagSerializer(many=True, read_only=True)
