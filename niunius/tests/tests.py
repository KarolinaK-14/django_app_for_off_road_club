from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

import pytest
from mixer.backend.django import mixer

from niunius import views
from niunius.forms import GuestForm
from niunius.models import CartItem


def test_home_view():
    request = RequestFactory().get("")
    response = views.HomeView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_view(logged_user, client):
    response = client.get(reverse("logout"))
    assert response.status_code == 302


def test_register_view():
    request = RequestFactory().get("")
    response = views.RegisterView.as_view()(request)
    assert response.status_code == 200


def test_register_view_if_missing_form_data(client):
    form = UserCreationForm(data={})
    response = client.post(reverse("register-user"))
    assert form.is_valid() is False
    assert response.status_code == 200


def test_contact_view():
    request = RequestFactory().get("")
    response = views.ContactView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_car_service_view():
    request = RequestFactory().get("")
    response = views.CarServiceView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_book_visit_view():
    request = RequestFactory().get("")
    response = views.BookVisitView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_blog_view():
    request = RequestFactory().get("")
    response = views.BlogView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_blog_view_if_articles_sorted_by_date_descending(client, articles):
    response = client.get(reverse("blog"))
    assert response.context["articles"][0] == articles[2]
    assert response.context["articles"][1] == articles[1]
    assert response.context["articles"][2] == articles[0]


@pytest.mark.django_db
def test_add_article_view(client, logged_user):
    response = client.get(reverse("add-article"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_article_view_if_unauthenticated_user():
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.AddArticleView.as_view()(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_update_article_view(client, logged_user):
    article = mixer.blend("niunius.Article")
    response = client.get(reverse("update-article", kwargs={"pk": article.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_article_view_if_unauthenticated_user():
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.UpdateArticleView.as_view()(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_comment_view(client, logged_user):
    article = mixer.blend("niunius.Article")
    response = client.get(reverse("add-comment", kwargs={"pk": article.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_comment_view_if_unauthenticated_user():
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.AddCommentView.as_view()(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_comment_view_if_comment_counter_works(client, logged_user, article):
    data = {"text": "test_text"}
    count = article.articlecomment_set.count()
    response = client.post(reverse("add-comment", kwargs={"pk": article.pk}), data=data)
    assert article.articlecomment_set.count() == count + 1
    assert response.status_code == 302


@pytest.mark.django_db
def test_article_detail_view(client):
    article = mixer.blend("niunius.Article")
    response = client.get(reverse("article-detail", kwargs={"slug": article.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_article_detail_view_like_button(client, article):
    count_like = article.like
    response = client.post(reverse("article-detail", kwargs={"slug": article.slug}))
    assert response.status_code == 200
    assert article.like >= count_like


@pytest.mark.django_db
def test_article_detail_view_dislike_button(client, article):
    count_dislike = article.dislike
    response = client.post(reverse("article-detail", kwargs={"slug": article.slug}))
    assert response.status_code == 200
    assert article.dislike >= count_dislike


@pytest.mark.django_db
def test_shop_view():
    request = RequestFactory().get("")
    response = views.ShopView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_shop__view_if_products_sorted_by_date_descending(client, products):
    response = client.get(reverse("shop"))
    assert response.context["latest_products"][0] == products[2]
    assert response.context["latest_products"][1] == products[1]
    assert response.context["latest_products"][2] == products[0]


@pytest.mark.django_db
def test_car_view(client):
    car = mixer.blend("niunius.Car", image="test.gif")
    response = client.get(reverse("car", kwargs={"slug": car.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_car_view_if_no_cars(client):
    response = client.get(reverse("car", kwargs={"slug": "test"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_view(client):
    category = mixer.blend("niunius.Category")
    response = client.get(reverse("category", kwargs={"slug": category.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_category_view_if_no_categories(client):
    response = client.get(reverse("category", kwargs={"slug": "test"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_product_view(client, product):
    response = client.get(reverse("product", kwargs={"slug": product.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_view_if_no_products(client):
    response = client.get(reverse("product", kwargs={"slug": "test"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_product_view_adding_to_shopping_cart(client, product):
    data = {"qty": 1}
    count = CartItem.objects.count()
    response = client.post(reverse("product", kwargs={"slug": product.slug}), data=data)
    assert response.status_code == 302
    assert CartItem.objects.count() == count + 1


@pytest.mark.django_db
def test_delete_item_view(client, product):
    item = mixer.blend("niunius.CartItem", product=product)
    response = client.post(reverse("delete-item", kwargs={"pk": item.pk}))
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_item_view_if_shopping_cart_items_changed(client, product):
    item = mixer.blend("niunius.CartItem", product=product)
    count = CartItem.objects.count()
    client.post(reverse("delete-item", kwargs={"pk": item.pk}))
    assert CartItem.objects.count() == count - 1


@pytest.mark.django_db
def test_shopping_cart_view():
    request = RequestFactory().get("")
    response = views.ShoppingCartView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_shopping_cart_view_changing_item_quantity(client, product):
    cart = mixer.blend("niunius.ShoppingCart")
    mixer.blend("niunius.CartItem", cart=cart, product=product)
    data = {"qty": 2, "product": product.id}
    response = client.post(reverse("shopping-cart"), data=data)
    assert response.status_code == 200
    assert response.context["items"][0].quantity == 2


@pytest.mark.django_db
def test_search_view(client):
    response = client.get("/szukaj/?query=test")
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_view_if_car_model_not_found(client):
    response = client.get("/szukaj/?query=test")
    assert len(response.context["cars"]) == 0


@pytest.mark.django_db
def test_search_view_if_car_model_found(client):
    mixer.blend("niunius.Car", model="test", image="test.gif")
    response = client.get("/szukaj/?query=test")
    assert len(response.context["cars"]) == 1


@pytest.mark.django_db
def test_order_view(client, logged_user):
    response = client.get(reverse("order"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_view_if_unauthenticated_user():
    with pytest.raises(Exception):
        request = RequestFactory().get("")
        request.user = AnonymousUser()
        views.OrderView.as_view()(request)


@pytest.mark.django_db
def tes_guest_order_view(client):
    response = client.get(reverse("guest-order"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_guest_order_view_if_missing_form_data(client):
    form = GuestForm(data={})
    response = client.post(reverse("guest-order"))
    assert form.is_valid() is False
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_confirmation_view(client, order):
    response = client.get(reverse("confirm-order", kwargs={"pk": order.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_order_confirmation_view_if_no_order(client):
    response = client.get(reverse("confirm-order", kwargs={"pk": 0}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_confirmation_view_buyer_in_context(client, order):
    response = client.get(reverse("confirm-order", kwargs={"pk": order.pk}))
    assert response.context["order"].buyer == order.buyer or None


@pytest.mark.django_db
def tes_purchase_view(client, order):
    response = client.get(reverse("purchase", kwargs={"pk": order.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_purchase_view_if_no_order(client):
    response = client.get(reverse("purchase", kwargs={"pk": 0}))
    assert response.status_code == 404
