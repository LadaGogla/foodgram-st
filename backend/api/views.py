# Стандартные библиотеки
from collections import defaultdict
from django.http import HttpResponse

# Сторонние библиотеки
from rest_framework import (
    viewsets, permissions, filters, status
)
from rest_framework.decorators import action
from rest_framework.response import Response

# Локальные импорты
from recipes.models import Ingredient, Recipe, Favourite, PurchaseList
from .serializers import (
    IngredientSerializer, RecipeSerializer,
    FavouriteSerializer, PurchaseSerializer
)
from recipes.permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly
from users.models import CustomUser, Follow
from users.serializers import (
    CustomUserSerializer, FollowSerializer,
    ChangePasswordSerializer, AvatarSerializer
)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__istartswith=name)
        return queryset

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favourite, created = Favourite.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                return Response({'status': 'Рецепт добавлен в избранное'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favourite.objects.filter(user=request.user, recipe=recipe).delete()
            if deleted:
                return Response({'status': 'Рецепт удален из избранного'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Рецепт не найден в избранном'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            purchase, created = PurchaseList.objects.get_or_create(user=request.user, recipe=recipe)
            if created:
                return Response({'status': 'Рецепт добавлен в список покупок'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'Рецепт уже в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = PurchaseList.objects.filter(user=request.user, recipe=recipe).delete()
            if deleted:
                return Response({'status': 'Рецепт удален из списка покупок'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Рецепт не найден в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchaseList.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='download', url_name='download')
    def download(self, request):
        ingredients = defaultdict(lambda: [0, ''])
        queryset = self.get_queryset().select_related(
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
                return Response({'status': f'Подписка на пользователя {user_to_follow.username} оформлена'}, status=status.HTTP_201_CREATED)
            return Response({'status': 'Вы уже подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Follow.objects.filter(follower=request.user, leader=user_to_follow).delete()
            if deleted:
                return Response({'status': f'Подписка на пользователя {user_to_follow.username} отменена'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'status': 'Вы не подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user) 