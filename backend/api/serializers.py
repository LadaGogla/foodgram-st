# Стандартные библиотеки
# (отсутствуют)

# Сторонние библиотеки
from rest_framework import serializers

# Локальные импорты
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.models import Follow
from users.serializers import CustomUserSerializer
from core.fields import Base64ImageField


# Константы для валидации
MIN_QUANTITY = 1
MAX_QUANTITY = 32_000


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
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
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()  
    author = CustomUserSerializer(read_only=True)  
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', 
        many=True,
        read_only=True
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(
        source='cook_time',
        required=True,
        min_value=1
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'ingredients', 'is_favorited', 
            'is_in_shopping_cart', 'name', 'image', 'text', 
            'cooking_time', 'tags'
        ]
        read_only_fields = ('author', 'ingredients', 'created_at')

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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        image_data = validated_data.pop('image')
    
        recipe = Recipe.objects.create(
            creator=self.context['request'].user,
            image=image_data,
            **validated_data
        )
    
    
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
    
    
        recipe.tags.set(tags_data)
    
        return recipe
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_data', None)
        base64_image_data = validated_data.pop('base64_image', None)
        if base64_image_data:
            instance.image = base64_image_data

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.cook_time = validated_data.get('cook_time', instance.cook_time)
        instance.save()

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=instance, **ingredient_data)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserWithRecipesSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUserSerializer.Meta.model
        fields = CustomUserSerializer.Meta.fields + ('is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit:
            try:
                queryset = queryset[:int(recipes_limit)]
            except ValueError:
                pass 
        return RecipeMinifiedSerializer(queryset, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, leader=obj).exists()
        return False 