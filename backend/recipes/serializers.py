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
    author = serializers.SerializerMethodField()
    name = serializers.CharField(source='title')
    products = DishProductSerializer(source='dishproduct_set', many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = ('id', 'author', 'name', 'description', 'image', 'products', 'cook_time', 'created_at')

    def get_author(self, obj):
        return {
            'id': obj.creator.id,
            'first_name': obj.creator.first_name,
            'last_name': obj.creator.last_name,
            'avatar': obj.creator.avatar.url if obj.creator.avatar else None
        }

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'dish')

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseList
        fields = ('id', 'user', 'dish') 