import pytest
from mixer.backend.django import mixer


@pytest.fixture
def order():
    order = mixer.blend("niunius.Order")
    return order


@pytest.fixture
def logged_user(client):
    user = mixer.blend("auth.User")
    client.force_login(user)
    return user


@pytest.fixture
def articles():
    a1 = mixer.blend("niunius.Article")
    a2 = mixer.blend("niunius.Article")
    a3 = mixer.blend("niunius.Article")
    return [a1, a2, a3]


@pytest.fixture
def article():
    article = mixer.blend("niunius.Article")
    return article


@pytest.fixture
def products():
    p1 = mixer.blend("niunius.Product", image="test.gif")
    p2 = mixer.blend("niunius.Product", image="test.gif")
    p3 = mixer.blend("niunius.Product", image="test.gif")
    return [p1, p2, p3]


@pytest.fixture
def product():
    product = mixer.blend("niunius.Product", image="test.gif")
    return product
