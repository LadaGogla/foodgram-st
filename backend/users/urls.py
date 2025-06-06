from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FollowViewSet

app_name = 'users' 

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'users/subscriptions', FollowViewSet, basename='subscription')

urlpatterns = [

    path(
        'users/me/avatar/',
        CustomUserViewSet.as_view({
            'put': 'set_avatar_me',
            'delete': 'delete_avatar_me'
        }),
        name='user-avatar'
    ),

    path('', include(router.urls)),
]