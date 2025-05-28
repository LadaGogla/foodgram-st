# Заглушка для urls.py приложения recipes
# Основная маршрутизация реализована во urls приложения api 

from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, DishViewSet, BookmarkViewSet, PurchaseListViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'dishes', DishViewSet, basename='dish')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'purchases', PurchaseListViewSet, basename='purchaselist')

urlpatterns = router.urls 