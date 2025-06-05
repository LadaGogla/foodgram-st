from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FollowViewSet

app_name = 'users' 

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = [
    # Explicit path for user avatar operations (/users/me/avatar/).
    # Placed at the beginning to ensure highest precedence.
    path(
        'users/me/avatar/',
        CustomUserViewSet.as_view({
            'put': 'set_avatar_me',
            'delete': 'delete_avatar_me'
        }),
        name='user-avatar'
    ),
    # Include router URLs after the explicit avatar path.
    path('', include(router.urls)),
]