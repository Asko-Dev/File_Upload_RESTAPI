from django.shortcuts import render
from rest_framework import generics, authentication, permissions,\
                           viewsets, mixins, status
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken

from .models import User, Tag, FileUpload
from .serializers import UserSerializer, AuthTokenSerializer, TagSerializer, \
                         FileUploadSerializer, FileUploadDetailSerializer


class UserView(generics.CreateAPIView):
    """Create a view for the user"""
    serializer_class = UserSerializer


class TokenView(ObtainAuthToken):
    """Create a view for the token claim"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Managed authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Return a user within ME URL"""
        return self.request.user


class TagViewSet(viewsets.ModelViewSet):
    """View for the Tag API"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class FileUploadViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = FileUploadSerializer
    queryset = FileUpload.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the autenticated user"""
        tags = self.request.query_params.get('tag')
        visibility = self.request.query_params.get('visibility')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tag__id__in=tag_ids)
        if visibility:
            queryset = queryset.filter(visibility=visibility)

        return queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return FileUploadDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class FileUploadPublicViewset(viewsets.ModelViewSet):
    """Public API for Public files"""
    serializer_class = FileUploadSerializer
    queryset = FileUpload.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'head']

    def _params_to_ints(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tag')
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tag__id__in=tag_ids)

        return queryset.filter(visibility='PUB').order_by('-id')
