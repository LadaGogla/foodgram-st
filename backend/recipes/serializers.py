from rest_framework import serializers
from .models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.serializers import CustomUserSerializer
from .fields import Base64ImageField

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('id', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(obj.recipeingredient_set.all(), many=True).data

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
        ingredients_data = self.context['request'].data.get('ingredients', [])
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

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe') 