from rest_framework import viewsets, permissions, filters, status
from .models import Ingredient, Recipe, RecipeIngredient, Favourite, PurchaseList
from .serializers import (
    IngredientSerializer, RecipeSerializer, RecipeIngredientSerializer,
    FavouriteSerializer, PurchaseListSerializer
)
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'author__username', 'tags__name']
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')

        if author:
            queryset = queryset.filter(author_id=author)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if is_favorited and self.request.user.is_authenticated:
            queryset = queryset.filter(favourites__user=self.request.user)
        if is_in_shopping_cart and self.request.user.is_authenticated:
            queryset = queryset.filter(purchase_lists__user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PurchaseListViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 