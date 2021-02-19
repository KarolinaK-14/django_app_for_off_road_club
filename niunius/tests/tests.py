from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

import pytest
from mixer.backend.django import mixer

from niunius import views, forms
from niunius.models import ArticleComment, CartItem


def test_home_view():
    request = RequestFactory().get("")
    response = views.HomeView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_view_by_logged_user(client, user):
    client.force_login(user)
    response = client.get(reverse("home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_blog_view():
    request = RequestFactory().get("")
    response = views.BlogView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_blog_view_if_articles_sorted_by_date_added_descending(client, articles):
    response = client.get(reverse("blog"))
    assert response.status_code == 200
    assert response.context["articles"][0] == articles[2]
    assert response.context["articles"][1] == articles[1]
    assert response.context["articles"][2] == articles[0]


@pytest.mark.django_db
def test_add_article_view_unauthenticated_user():
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.ArticleAddView.as_view()(request)
    assert response.status_code == 302


def test_add_article_view_missing_form_data():
    form = forms.OrderForm(data={})
    assert form.is_valid() is False


@pytest.mark.django_db
def test_add_comment_view_unauthenticated_user(article):
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.CommentAddView.as_view()(request, pk=article.pk)
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_comment_view_authenticated_user(user, article, client):
    client.force_login(user)
    response_get = client.get(reverse("add-comment", kwargs={"pk": article.pk}))
    assert response_get.status_code == 200

    data = {"text": "test_text"}
    count = ArticleComment.objects.count()
    response_post = client.post(
        reverse("add-comment", kwargs={"pk": article.pk}), data=data
    )
    assert ArticleComment.objects.count() == count + 1
    assert response_post.status_code == 302


@pytest.mark.django_db
def test_article_detail_view(article, client):
    response = client.get(reverse("article-detail", kwargs={"slug": article.slug}))
    assert response.status_code == 200
    assert response.context["article"].title == article.title
    assert response.context["article"].slug == article.slug
    assert response.context["article"].content == article.content
    assert response.context["article"].user == article.user
    assert response.context["article"].added == article.added
    assert response.context["article"].like == article.like
    assert response.context["article"].dislike == article.dislike


@pytest.mark.django_db
def test_article_detail_view_like_button(article, client):
    count_like = article.like
    response = client.post(reverse("article-detail", kwargs={"slug": article.slug}))
    assert response.status_code == 200
    assert article.like >= count_like


@pytest.mark.django_db
def test_article_detail_view_dislike_button(article, client):
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
def test_shop_if_products_sorted_by_date_added_descending(client, products):
    response = client.get(reverse("shop"))
    assert response.status_code == 200
    assert response.context["latest_products"][0] == products[2]
    assert response.context["latest_products"][1] == products[1]
    assert response.context["latest_products"][2] == products[0]


@pytest.mark.django_db
def test_car_view(car, client):
    response = client.get(reverse("car", kwargs={"slug": car.slug}))
    assert response.status_code == 200
    assert response.context["car"].brand == car.brand
    assert response.context["car"].model == car.model
    assert response.context["car"].slug == car.slug
    assert response.context["car"].image == car.image


@pytest.mark.django_db
def test_car_view_if_no_cars(client):
    response = client.get(reverse("car", kwargs={"slug": "test"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_view(category, client):
    response = client.get(reverse("category", kwargs={"slug": category.slug}))
    assert response.status_code == 200
    assert response.context["category"].name == category.name
    assert response.context["category"].slug == category.slug


@pytest.mark.django_db
def test_category_view_if_no_category(client):
    response = client.get(reverse("category", kwargs={"slug": "test"}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_product_view(product, client):
    response = client.get(reverse("product", kwargs={"slug": product.slug}))
    assert response.status_code == 200
    assert response.context["product"].name == product.name
    assert response.context["product"].slug == product.slug
    assert response.context["product"].added == product.added
    assert response.context["product"].code == product.code
    assert response.context["product"].stock == product.stock
    assert response.context["product"].description == product.description
    assert response.context["product"].price == product.price
    assert response.context["product"].image == product.image


@pytest.mark.django_db
def test_add_product_to_shopping_cart(product, client):
    data = {"qty": 1}
    count = CartItem.objects.count()
    response = client.post(reverse("product", kwargs={"slug": product.slug}), data=data)
    assert response.status_code == 302
    assert CartItem.objects.count() == count + 1


@pytest.mark.django_db
def test_delete_item_view(client, product):
    item = mixer.blend("niunius.CartItem", product=product)
    count = CartItem.objects.count()
    client.post(reverse("delete-item", kwargs={"pk": item.pk}))
    assert CartItem.objects.count() == count - 1


@pytest.mark.django_db
def test_delete_item_view_redirect_to_shopping_cart(client, product):
    item = mixer.blend("niunius.CartItem", product=product)
    response = client.post(reverse("delete-item", kwargs={"pk": item.pk}))
    assert response.status_code == 302
    assert "/sklep/koszyk/" in response.url


@pytest.mark.django_db
def test_shopping_cart_view(client):
    response = client.get(reverse("cart"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_shopping_cart_view_change_item_quantity(product, client):
    cart = mixer.blend("niunius.ShoppingCart")
    session = client.session
    session["cart"] = cart.id
    session.save()
    mixer.blend("niunius.CartItem", cart=cart, product=product)
    data = {"qty": 2, "product": product.id}
    response = client.post(reverse("cart"), data=data)
    assert response.status_code == 200
    assert response.context["items"][0].quantity == 2


@pytest.mark.django_db
def test_search_view(client):
    response = client.get("/szukaj/?query=test")
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_view_no_matchings_for_query(client):
    response = client.get("/szukaj/?query=test")
    print(response.context)
    assert len(response.context["cars"]) == 0


@pytest.mark.django_db
def test_search_view_if_matchings_for_query(client):
    mixer.blend("niunius.Car", model="test", image="test.gif")
    response = client.get("/szukaj/?query=test")
    print(response.context)
    assert len(response.context["cars"]) == 1


@pytest.mark.django_db
def test_user_creation_view():
    request = RequestFactory().get("")
    response = views.UserCreationView.as_view()(request)
    assert response.status_code == 200


def test_user_creation_view_missing_form_data():
    form = UserCreationForm(data={})
    assert form.is_valid() is False


@pytest.mark.django_db
def test_order_view_unauthenticated_user():
    request = RequestFactory().get("")
    request.user = AnonymousUser()
    response = views.OrderView.as_view()(request)
    assert response.status_code == 302


def test_order_view_missing_form_data():
    form = forms.OrderForm(data={})
    assert form.is_valid() is False


@pytest.mark.django_db
def test_confirmation_view_status_code():
    order = mixer.blend("niunius.Order")
    request = RequestFactory().get("", pk=order.pk)
    response = views.ConfirmationView.as_view()(request, pk=order.pk)
    assert response.status_code == 200


@pytest.mark.django_db
def test_confirmation_view_context(client):
    order = mixer.blend("niunius.Order")
    response = client.get(reverse("confirmation", kwargs={"pk": order.pk}))
    assert response.context["order"].address_city == order.address_city
