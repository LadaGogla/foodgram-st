# Заглушка для urls.py приложения users
# Основная маршрутизация реализована во urls приложения api 

from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, FollowViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = router.urls 