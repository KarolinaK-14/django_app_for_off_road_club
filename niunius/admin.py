from django.contrib import admin
from .models import Article, ArticlePhoto, ArticleComment, Product, Car, Category


class ArticlePhotoInLine(admin.TabularInline):
    model = ArticlePhoto


class ArticleCommentInLine(admin.TabularInline):
    model = ArticleComment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticlePhotoInLine, ArticleCommentInLine]


@admin.register(ArticlePhoto)
class ArticlePhotoAdmin(admin.ModelAdmin):
    pass


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
