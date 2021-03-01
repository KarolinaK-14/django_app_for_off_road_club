from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

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


class MyAdminSite(AdminSite):
    site_header = "Niuniuś"


admin_site = MyAdminSite(name="myadmin")

admin_site.register(User)
admin_site.register(ArticlePhoto)
admin_site.register(ArticleComment)
admin_site.register(CarService)


class ArticlePhotoInLine(admin.TabularInline):
    model = ArticlePhoto


class ArticleCommentInLine(admin.TabularInline):
    model = ArticleComment


class CartItemInLine(admin.TabularInline):
    model = CartItem


@admin.register(Article, site=admin_site)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticlePhotoInLine, ArticleCommentInLine]
    exclude = ["slug"]


@admin.register(Car, site=admin_site)
class CarAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    exclude = ["slug"]


@admin.register(ShoppingCart, site=admin_site)
class ShoppingCartAdmin(admin.ModelAdmin):
    inlines = [CartItemInLine]


@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    exclude = ["cart"]
