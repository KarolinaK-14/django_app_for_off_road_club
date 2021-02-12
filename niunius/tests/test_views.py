import pytest
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer
from django.test import RequestFactory
from django.urls import reverse
from niunius import views
from niunius.models import Article


@pytest.mark.django_db
def test_home_view_unauthenticated():
    req = RequestFactory().get('')
    resp = views.HomeView.as_view()(req)
    assert resp.status_code == 200, "Should be callable by anyone"


@pytest.mark.django_db
def test_add_article_view_unauthenticated():
    req = RequestFactory().get('')
    req.user = AnonymousUser()
    resp = views.ArticleAddView.as_view()(req)
    assert 'login' in resp.url, "Unauthenticated user cannot access and should be redirect to login page"


@pytest.mark.django_db
class TestAddArticle:
    def test_get_if_user_authenticated(self):
        user = mixer.blend('auth.User', is_superuser=True)
        req = RequestFactory().get('')
        req.user = user
        resp = views.ArticleAddView.as_view()(req)
        assert resp.status_code == 200, "Authenticated user can access"

    def test_post(self, user):
        data = {
            "title": "tytul",
            "slug": "tytul",
            "content": "tresc",
            "user": user,
            "added": "2020-10-15T22:17:44Z",
            "like": 2,
            "dislike": 5,
        }
        req = RequestFactory().post('', data=data)
        Article.objects.create(
            title="tytul",
            slug="tytul",
            content="tresc",
            user=user,
            added="2020-10-15T22:17:44Z",
            like=2,
            dislike=5,
        )
        count = Article.objects.count()
        resp = views.ArticleAddView.as_view()(req)
        assert resp.status_code == 302
        assert 'blog' in resp.url, "Should redirect to blog page"
        assert Article.objects.count() == count + 1, "Should create a new Article instance"


@pytest.mark.django_db
def test_add_comment_view_unauthenticated():
    article = mixer.blend('niunius.Article', title='tytul')
    req = RequestFactory().get('')
    req.user = AnonymousUser()
    resp = views.CommentAddView.as_view()(req, slug=article.slug)
    assert 'login' in resp.url, "Unauthenticated user cannot access and should be redirect to login page"


@pytest.mark.django_db
def test_add_comment_view_authenticated():
    user = mixer.blend('auth.User', is_superuser=True)
    article = mixer.blend('niunius.Article', title='tytul')
    req = RequestFactory().get('')
    req.user = user
    resp = views.CommentAddView.as_view()(req, slug=article.slug)
    assert resp.status_code == 200, "Authenticated user can access"


@pytest.mark.django_db
def test_category_view(category, client):
    response = client.get(reverse("category", kwargs={"slug": category.slug}))
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
