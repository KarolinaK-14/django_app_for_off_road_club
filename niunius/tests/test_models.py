from niunius.models import OrderItem, Order
from mixer.backend.django import mixer
import pytest


@pytest.mark.django_db
class TestModel:
    def test_model_article(self):
        obj = mixer.blend('niunius.Article')
        assert obj.pk == 1, "Should create an Article instance"

    def test_model_article_photo(self):
        obj = mixer.blend('niunius.ArticlePhoto')
        assert obj.pk == 1, "Should create an ArticlePhoto instance"

    def test_model_article_comment(self):
        obj = mixer.blend('niunius.ArticleComment')
        assert obj.pk == 1, "Should create an ArticleComment instance"

    def test_model_car(self):
        obj = mixer.blend('niunius.Car')
        assert obj.pk == 1, "Should create a Car instance"

    def test_model_category(self):
        obj = mixer.blend('niunius.Category')
        assert obj.pk == 1, "Should create a Category instance"

    def test_model_product(self):
        obj = mixer.blend('niunius.Product')
        assert obj.pk == 1, "Should create a Product instance"

    def test_model_order(self):
        obj = mixer.blend('niunius.Order')
        assert obj.pk == 1, "Should create an Order instance"

    def test_create_order_item_instance(self):
        obj = mixer.blend('niunius.OrderItem')
        assert obj.pk == 1, "Should create an OrderItem instance"


@pytest.mark.django_db
def test_order_total():
    product1 = mixer.blend('niunius.Product', price=1)
    product2 = mixer.blend('niunius.Product', price=2)
    order = mixer.blend('niunius.Order')
    mixer.blend('niunius.OrderItem', product=product1, order=order, quantity=3)
    mixer.blend('niunius.OrderItem', product=product2, order=order, quantity=4)
    assert order.order_total() == 11, "Should sum values of order items"


@pytest.mark.django_db
def test_get_order_item_value():
    product = mixer.blend('niunius.Product', price=1)
    item = mixer.blend('niunius.OrderItem', product=product, quantity=2)
    assert item.value == 2, "Should calculate the value as quantity multiplied by product price."
