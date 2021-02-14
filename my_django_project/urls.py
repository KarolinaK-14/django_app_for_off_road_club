"""my_django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings
from niunius import views as v

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", v.HomeView.as_view(), name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("rejestracja/", v.UserCreationView.as_view(), name="signup"),
    path("blog/", v.BlogView.as_view(), name="blog"),
    path("blog/dodaj-artykul/", v.ArticleAddView.as_view(), name="add-article"),
    path("blog/artykul/<slug:slug>/", v.ArticleDetailView.as_view(), name="article-detail"),
    path("blog/artykul/<slug:slug>/dodaj-komentarz/", v.CommentAddView.as_view(), name="add-comment"),
    path("sklep/", v.ShopView.as_view(), name="shop"),
    path("sklep/auto/<slug:slug>/", v.CarView.as_view(), name="car"),
    path("sklep/kategoria/<slug:slug>/", v.CategoryView.as_view(), name="category"),
    path("sklep/produkt/<slug:slug>/", v.ProductView.as_view(), name="product"),
    path("sklep/koszyk/", v.ShoppingCartView.as_view(), name="cart"),
    path("sklep/koszyk/usun/<int:pk>/", v.DeleteItemView.as_view(), name="delete-item"),
    path("szukaj/", v.SearchView.as_view(), name="search"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
