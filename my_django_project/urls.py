from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from niunius import views as v
from niunius.admin import admin_site
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("myadmin/", admin_site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", v.HomeView.as_view(), name="home"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path(
        "zmiana-hasla/",
        v.PasswordsChangeView.as_view(
            template_name="registration/change_password.html"
        ),
        name="change-password",
    ),
    path("register/", v.RegisterView.as_view(), name="register"),
    path("edytuj-profil/", v.UserChangeView.as_view(), name="edit-profile"),
    path("moje-zamowienia/", v.UserOrdersView.as_view(), name="user-orders"),
    path("o-klubie/", v.AboutView.as_view(), name="about"),
    path("kontakt/", v.ContactView.as_view(), name="contact"),
    path("warsztat/", v.CarServiceView.as_view(), name="car-service"),
    path("warsztat-wizyta/", v.BookVisitView.as_view(), name="book-visit"),
    path("blog/", v.BlogView.as_view(), name="blog"),
    path("blog/dodaj-artykul/", v.AddArticleView.as_view(), name="add-article"),
    path(
        "blog/zmien-artykul/<int:pk>/",
        v.UpdateArticleView.as_view(),
        name="update-article",
    ),
    path(
        "blog/artykul/<slug:slug>/",
        v.ArticleDetailView.as_view(),
        name="article-detail",
    ),
    path(
        "blog/artykul/<int:pk>/dodaj-komentarz/",
        v.AddCommentView.as_view(),
        name="add-comment",
    ),
    path("sklep/", v.ShopView.as_view(), name="shop"),
    path("sklep/szukaj/", v.SearchView.as_view(), name="search"),
    path("sklep/auto/<slug:slug>/", v.CarView.as_view(), name="car"),
    path("sklep/kategoria/<slug:slug>/", v.CategoryView.as_view(), name="category"),
    path("sklep/produkt/<slug:slug>/", v.ProductView.as_view(), name="product"),
    path("sklep/koszyk/", v.ShoppingCartView.as_view(), name="shopping-cart"),
    path(
        "sklep/koszyk/usun-produkt/<int:pk>/",
        v.DeleteItemView.as_view(),
        name="delete-item",
    ),
    path("sklep/zamowienie/", v.OrderView.as_view(), name="order"),
    path("sklep/zamowienie-gosc/", v.GuestOrderView.as_view(), name="guest-order"),
    path(
        "sklep/potwierdz-zamowienie/<int:pk>/",
        v.OrderConfirmationView.as_view(),
        name="confirm-order",
    ),
    path("sklep/potwierd-zakup/<int:pk>/", v.PurchaseView.as_view(), name="purchase"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
