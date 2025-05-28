from rest_framework import viewsets, permissions, filters
from .models import Product, Dish, Bookmark, PurchaseList
from .serializers import ProductSerializer, DishSerializer, BookmarkSerializer, PurchaseListSerializer
from .permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly
from django.http import HttpResponse
from collections import defaultdict
from rest_framework.decorators import action

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

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