from django.urls import path, include
from rest_framework.routers import DefaultRouter

from files import views


app_name = 'files'

router = DefaultRouter()
router.register('tag', views.TagViewSet)
router.register('file-upload', views.FileUploadViewSet)
router.register(
    'public-files',
    views.FileUploadPublicViewset,
    basename='public'
)

urlpatterns = [
    path('user-create/', views.UserView.as_view(), name='user-create'),
    path('user-token/', views.TokenView.as_view(), name='user-token'),
    path('user-me/', views.ManagerUserView.as_view(), name='user-me'),
    path('', include(router.urls))
]
