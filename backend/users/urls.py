from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FollowViewSet

app_name = 'users' 

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]