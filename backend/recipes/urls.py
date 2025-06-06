# Стандартные библиотеки
# (отсутствуют)

# Сторонние библиотеки
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Локальные импорты
from .views import (
    IngredientViewSet, RecipeViewSet,
    FavoriteViewSet, ShoppingCartViewSet
)


router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'favourites', FavoriteViewSet, basename='favourite')
router.register(r'purchase-list', ShoppingCartViewSet, basename='purchase-list')

urlpatterns = router.urls 