# Стандартные библиотеки
# (отсутствуют)

# Сторонние библиотеки
from rest_framework import serializers

# Локальные импорты
from recipes.models import Product, Dish, DishProduct, Bookmark, PurchaseList
from core.fields import Base64ImageField


# Константы для валидации
MIN_QUANTITY = 1
MAX_QUANTITY = 32_000


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'unit')


class DishProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    amount = serializers.IntegerField(
        source='quantity',
        min_value=MIN_QUANTITY,
        max_value=MAX_QUANTITY,
        error_messages={
            'min_value': f'Минимальное количество — {MIN_QUANTITY}',
            'max_value': f'Максимальное количество — {MAX_QUANTITY}'
        }
    )

    class Meta:
        model = DishProduct
        fields = ('product', 'product_id', 'amount')


class DishSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    name = serializers.CharField(source='title')
    products = DishProductSerializer(
        source='dishproduct_set',
        many=True,
        read_only=True
    )
    ingredients = DishProductSerializer(
        many=True,
        write_only=True
    )
    base64_image = Base64ImageField(required=False, allow_null=True, write_only=True)
    image = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        source='cook_time',
        min_value=MIN_QUANTITY,
        max_value=MAX_QUANTITY,
        error_messages={
            'min_value': f'Минимальное время приготовления — {MIN_QUANTITY} минута',
            'max_value': f'Максимальное время приготовления — {MAX_QUANTITY} минут'
        }
    )

    class Meta:
        model = Dish
        fields = (
            'id', 'author', 'name', 'description', 'image',
            'products', 'ingredients', 'cooking_time', 'created_at', 'base64_image'
        )
        read_only_fields = ('author', 'products', 'created_at')

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

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        base64_image_data = validated_data.pop('base64_image', None)
        if base64_image_data:
            validated_data['image'] = base64_image_data

        dish = Dish.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            DishProduct.objects.create(dish=dish, **ingredient_data)
        return dish

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        base64_image_data = validated_data.pop('base64_image', None)
        if base64_image_data:
            instance.image = base64_image_data

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.cook_time = validated_data.get('cook_time', instance.cook_time)
        instance.save()

        if ingredients_data is not None:
            instance.dishproduct_set.all().delete()
            for ingredient_data in ingredients_data:
                DishProduct.objects.create(dish=instance, **ingredient_data)

        return instance


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'dish')


class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseList
        fields = ('id', 'user', 'dish') 