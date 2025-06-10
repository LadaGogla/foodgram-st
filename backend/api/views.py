# Стандартные библиотеки
from collections import defaultdict
from django.http import HttpResponse

# Сторонние библиотеки
from rest_framework import (
    viewsets, permissions, filters, status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.pagination import LimitOffsetPagination

# Локальные импорты
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    FavoriteSerializer, ShoppingCartSerializer,
    UserWithRecipesSerializer,
    RecipeMinifiedSerializer 
)
from recipes.permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly
from users.models import CustomUser, Follow
from users.serializers import (
    CustomUserSerializer, FollowSerializer,
    ChangePasswordSerializer, AvatarSerializer
)
from core.fields import Base64ImageField

class RecipeLimitPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__startswith=name)
        return queryset




class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser] 
    pagination_class = RecipeLimitPagination 
    
    def get_queryset(self):
        queryset = self.queryset
        author_id = self.request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(creator=author_id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ['1', 'true'] and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart in ['1', 'true'] and self.request.user.is_authenticated:
            queryset = queryset.filter(shoppingcart__user=self.request.user)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite_obj, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                serializer = RecipeMinifiedSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            if deleted:
                return Response({'status': 'Рецепт удален из избранного'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            shopping_cart_obj, created = ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                serializer = RecipeMinifiedSerializer(recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status': 'Рецепт уже в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
            if deleted:
                return Response({'status': 'Рецепт удален из списка покупок'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Рецепт не найден в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart', url_name='download_shopping_cart', permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = defaultdict(lambda: [0, ''])
        queryset = ShoppingCart.objects.filter(user=request.user).select_related(
            'recipe'
        ).prefetch_related(
            'recipe__recipeingredient_set__ingredient'
        ).values(
            'recipe__recipeingredient__ingredient__name',
            'recipe__recipeingredient__ingredient__measurement_unit',
            'recipe__recipeingredient__quantity'
        ).order_by('recipe__recipeingredient__ingredient__name')

        for item in queryset:
            name = item['recipe__recipeingredient__ingredient__name']
            unit = item['recipe__recipeingredient__ingredient__measurement_unit']
            quantity = item['recipe__recipeingredient__quantity']
            ingredients[(name, unit)][0] += quantity
            ingredients[(name, unit)][1] = unit

        lines = [
            f'{name} ({unit}) — {amount}'
            for (name, unit), (amount, _) in ingredients.items()
        ]
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

class FollowViewSet(viewsets.ModelViewSet):
    
    serializer_class = UserWithRecipesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    http_method_names = ['get']

    def get_queryset(self):
        
        return CustomUser.objects.filter(following__follower=self.request.user)

class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='set_password')
    def set_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Неверный текущий пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'status': 'Пароль успешно изменён.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='set_avatar')
    def set_avatar(self, request):
        serializer = AvatarSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Аватар обновлён.', 'avatar': serializer.data['avatar']})

    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated], url_path='delete_avatar')
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response({'status': 'Аватар удалён.'})

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object() 
        if request.user == user_to_follow:
             return Response({'errors': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            follow, created = Follow.objects.get_or_create(follower=request.user, leader=user_to_follow)
            if created:
                
                serializer = UserWithRecipesSerializer(user_to_follow, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status': 'Вы уже подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Follow.objects.filter(follower=request.user, leader=user_to_follow).delete()
            if deleted:
                return Response({'status': f'Подписка на пользователя {user_to_follow.username} отменена'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Вы не подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST) 