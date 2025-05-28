# В этом файле только объединение роутеров из users и recipes

from rest_framework import viewsets, permissions, filters
from recipes.models import Product, Dish, Bookmark, PurchaseList
from recipes.serializers import ProductSerializer, DishSerializer, BookmarkSerializer, PurchaseListSerializer
from users.models import CustomUser, Follow
from users.serializers import CustomUserSerializer, FollowSerializer, ChangePasswordSerializer, AvatarSerializer
from django.http import HttpResponse
from collections import defaultdict
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from recipes.permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PurchaseListViewSet(viewsets.ModelViewSet):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='download', url_name='download')
    def download(self, request):
        # Агрегируем продукты из всех блюд в списке покупок пользователя
        ingredients = defaultdict(lambda: [0, ''])
        for item in self.get_queryset():
            for dp in item.dish.dishproduct_set.all():
                name = dp.product.name
                unit = dp.product.unit
                ingredients[(name, unit)][0] += dp.quantity
                ingredients[(name, unit)][1] = unit
        lines = [f'{name} ({unit}) — {amount}' for (name, unit), (amount, _) in ingredients.items()]
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
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
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Неверный текущий пароль.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'Пароль успешно изменён.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='set_avatar')
    def set_avatar(self, request):
        serializer = AvatarSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Аватар обновлён.', 'avatar': serializer.data['avatar']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated], url_path='delete_avatar')
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response({'status': 'Аватар удалён.'})

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(follower=self.request.user)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user) 