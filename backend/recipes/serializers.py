from rest_framework import serializers
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.models import CustomUser
from .fields import Base64ImageField

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscribers.filter(user=request.user).exists()
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class RecipeAuthorSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        pass


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    author = RecipeAuthorSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            obj.recipeingredient_set.all(), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Список ингредиентов не может быть пустым.')

        ingredient_ids = [item['id'] for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не должны повторяться.')

        for item in value:
            serializer = IngredientInRecipeSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise serializers.ValidationError(f'Ингредиент с id={item["id"]} не существует.')
        return value

    def create(self, validated_data):
        ingredients_data = self.context['request'].data.get('ingredients', [])
        self.validate_ingredients(ingredients_data)
        image_data = validated_data.pop('image')

        recipe = Recipe.objects.create(image=image_data, **validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.context['request'].data.get('ingredients', [])
        self.validate_ingredients(ingredients_data)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if ingredients_data:
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient_data['id'],
                    amount=ingredient_data['amount']
                )
        
        instance.save()
        return instance

class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeMinifiedSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeMinifiedSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe') 