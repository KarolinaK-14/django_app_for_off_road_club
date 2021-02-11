from django.contrib.auth.models import User
from niunius.models import Article, Car, Category
import pytest
import tempfile


@pytest.fixture
def user():
    username = "user1"
    password = "user1"
    user = User.objects.create_user(username=username, password=password)
    return user


@pytest.fixture
def article():
    username = "user1"
    password = "user1"
    user = User.objects.create_user(username=username, password=password)
    return Article.objects.create(
        title="tytul",
        slug="tytul",
        content="tresc",
        user=user,
        added="2021-05-05",
        like=2,
        dislike=5,
    )


@pytest.fixture
def articles():
    username = "user1"
    password = "user1"
    user = User.objects.create_user(username=username, password=password)
    a1 = Article.objects.create(
        title="tytul1",
        slug="tytul1",
        content="tresc1",
        user=user,
        added="2021-05-07 10:10",
        like=0,
        dislike=0,
    )
    a2 = Article.objects.create(
        title="tytul2",
        slug="tytul2",
        content="tresc2",
        user=user,
        added="2021-05-06 11:11",
        like=2,
        dislike=2,
    )
    a3 = Article.objects.create(
        title="tytul3",
        slug="tytul3",
        content="tresc3",
        user=user,
        added="2021-05-05 12:12",
        like=4,
        dislike=4,
    )
    return [a1, a2, a3]


@pytest.fixture
def category():
    return Category.objects.create(name="nazwa", slug="nazwa")


@pytest.fixture
def car():
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Car.objects.create(
        brand="marka", model="model", slug="marka-model", image=image
    )
