from django.contrib import admin
from .models import (
    Article,
    ArticlePhoto,
    ArticleComment,
    Car,
    Category,
    Product,
    ShoppingCart,
    CartItem,
    Order,
    CarService,
)


class ArticlePhotoInLine(admin.TabularInline):
    model = ArticlePhoto


class ArticleCommentInLine(admin.TabularInline):
    model = ArticleComment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticlePhotoInLine, ArticleCommentInLine]
    exclude = ["slug"]


@admin.register(ArticlePhoto)
class ArticlePhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    exclude = ["cart"]


@admin.register(CarService)
class CarServiceAdmin(admin.ModelAdmin):
    pass
