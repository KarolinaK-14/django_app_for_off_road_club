import pytest
from django.urls import reverse
from niunius.models import Article


@pytest.mark.django_db
def test_category_view(category, client):
    response = client.get(reverse("category", kwargs={"slug": category.slug}))
    # print(response.context)
    assert response.status_code == 200
    assert response.context["category"].name == category.name
    assert response.context["category"].slug == category.slug


@pytest.mark.django_db
def test_article_view(article, client):

    response = client.get(reverse("article-detail", kwargs={"slug": article.slug}))
    # import pdb;
    # pdb.set_trace()
    assert response.status_code == 200
    assert response.context["article"].title == article.title
    assert response.context["article"].slug == article.slug
    assert response.context["article"].content == article.content
    assert response.context["article"].user == article.user
    assert response.context["article"].added == article.added
    assert response.context["article"].like == article.like
    assert response.context["article"].dislike == article.dislike


@pytest.mark.django_db
def test_add_article(client, user):
    client.force_login(user)
    ctx = {
        "title": "tytul",
        "content": "tresc",
    }
    response = client.post(reverse("add-article"), ctx)
    count = Article.objects.count()
    article = Article.objects.create(title="nowy tytul", content="tresc", user=user)
    assert article is not None
    assert Article.objects.count() == count + 1
    assert response.status_code == 302


@pytest.mark.django_db
def test_articles_list(articles, client):
    response = client.get(reverse("blog"))
    assert response.status_code == 200
    assert response.context["articles"][0] == articles[2]
    assert response.context["articles"][1] == articles[1]
    assert response.context["articles"][2] == articles[0]


@pytest.mark.django_db
def test_car_view(car, client):
    response = client.get(reverse("car", kwargs={"slug": car.slug}))
    assert response.status_code == 200
    assert response.context["car"].brand == car.brand
    assert response.context["car"].model == car.model
    assert response.context["car"].slug == car.slug
    assert response.context["car"].image == car.image
