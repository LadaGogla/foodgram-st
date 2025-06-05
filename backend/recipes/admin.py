from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Favourite, PurchaseList

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email')
    inlines = [RecipeIngredientInline]
    readonly_fields = ('count_in_favourites',)

    def count_in_favourites(self, obj):
        return obj.favourites.count()
    count_in_favourites.short_description = 'В избранном'

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__title')

@admin.register(PurchaseList)
class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__title')

