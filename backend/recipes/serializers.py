from rest_framework import serializers
from .models import Product, Dish, DishProduct, Bookmark, PurchaseList

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit')

class DishProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = DishProduct
        fields = ('product', 'product_id', 'quantity')

class DishSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    products = DishProductSerializer(source='dishproduct_set', many=True, read_only=True)
    image = serializers.ImageField()

    class Meta:
        model = Dish
        fields = ('id', 'creator', 'title', 'description', 'image', 'products', 'cook_time', 'created_at')

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'dish')

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseList
        fields = ('id', 'user', 'dish') 