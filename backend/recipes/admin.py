from django.contrib import admin
from .models import Product, Dish, DishProduct, Bookmark, PurchaseList

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)

class DishProductInline(admin.TabularInline):
    model = DishProduct
    extra = 1

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email')
    inlines = [DishProductInline]
    readonly_fields = ('count_in_bookmarks',)

    def count_in_bookmarks(self, obj):
        return obj.bookmarks.count()
    count_in_bookmarks.short_description = 'В избранном'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish')
    search_fields = ('user__username', 'dish__title')

@admin.register(PurchaseList)
class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish')
    search_fields = ('user__username', 'dish__title')

# DishProduct не регистрируем отдельно, только inline 