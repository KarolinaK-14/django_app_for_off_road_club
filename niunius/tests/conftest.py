import pytest
from mixer.backend.django import mixer

from niunius.models import Article, Product


@pytest.fixture
def user():
    return mixer.blend("auth.User")


@pytest.fixture
def article():
    user = mixer.blend("auth.User")
    return Article.objects.create(
        title="test_title",
        content="test_content",
        user=user,
        added="2020-10-15T22:17:44Z",
        like=2,
        dislike=5,
    )


@pytest.fixture
def articles():
    user = mixer.blend("auth.User")
    a1 = Article.objects.create(
        title="test title 1",
        slug="test-title-1",
        content="test_content",
        user=user,
        added="",
        like=0,
        dislike=0,
    )
    a2 = Article.objects.create(
        title="test_title_2",
        slug="test-title-2",
        content="test_content_2",
        user=user,
        added="",
        like=2,
        dislike=2,
    )
    a3 = Article.objects.create(
        title="test_title_3",
        slug="test-title-3",
        content="test_content_3",
        user=user,
        added="",
        like=4,
        dislike=4,
    )
    return [a1, a2, a3]


@pytest.fixture
def category():
    return mixer.blend("niunius.Category")


@pytest.fixture
def car():
    return mixer.blend("niunius.Car", image="test.gif")


@pytest.fixture
def product():
    return mixer.blend("niunius.Product", image="test.gif")


@pytest.fixture
def products():
    p1 = Product.objects.create(
        name="test name 1",
        code="abc1",
        stock=1,
        description="test description 1",
        price=9.99,
        image="test.gif",
    )
    p2 = Product.objects.create(
        name="test name 2",
        code="abc2",
        stock=2,
        description="test description 2",
        price=19.99,
        image="test.gif",
    )
    p3 = Product.objects.create(
        name="test name 3",
        code="abc3",
        stock=3,
        description="test description 3",
        price=29.99,
        image="test.gif",
    )
    return [p1, p2, p3]
