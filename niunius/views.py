from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, TemplateView
from .forms import ArticleForm, ArticleCommentForm
from .models import (
    Article,
    ArticlePhoto,
    ArticleComment,
    Car,
    Category,
    Product,
    Order,
    OrderItem,
)


class HomeView(TemplateView):
    template_name = "niunius/base.html"


class BlogView(View):
    def get(self, request):
        articles = Article.objects.all().order_by("-added")
        paginator = Paginator(articles, 1)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        ctx = {"articles": articles, "page_obj": page_obj}
        return render(request, "niunius/blog.html", ctx)


class ArticleAddView(View):
    def get(self, request):
        form = ArticleForm()
        ctx = {"form": form}
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % ("/accounts/login/", request.path))
        return render(request, "niunius/article_form.html", ctx)

    def post(self, request):
        form = ArticleForm(request.POST, request.FILES)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            article = Article.objects.create(
                title=title, content=content, user=request.user
            )
            for photo in request.FILES.getlist("photos"):
                ArticlePhoto.objects.create(photo=photo, article=article)
            return redirect("blog")

        ctx = {"form": form}
        return render(request, "niunius/article_form.html", ctx)


class CommentAddView(View):
    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        form = ArticleCommentForm()
        ctx = {"form": form, "article": article}
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % ("/accounts/login/", request.path))
        return render(request, "niunius/article_comment_form.html", ctx)

    def post(self, request, slug):
        form = ArticleCommentForm(request.POST)
        article = get_object_or_404(Article, slug=slug)
        if form.is_valid():
            text = form.cleaned_data["text"]
            ArticleComment.objects.create(article=article, text=text, user=request.user)
            return redirect("article-detail", article.slug)
        ctx = {
            "form": form,
            "article": article,
        }
        return redirect("add-comment", ctx)


class ArticleDetailView(View):
    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        form = ArticleCommentForm()
        comments = article.articlecomment_set.all().order_by("-added")
        comments_count = comments.count()
        ctx = {
            "article": article,
            "comments": comments,
            "comments_count": comments_count,
            "form": form,
        }

        return render(request, "niunius/article_detail.html", ctx)

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        comments = article.articlecomment_set.all().order_by("-added")
        comments_count = comments.count()

        if "like" in request.POST:
            article.like = F("like") + 1
            article.save()
            return redirect("article-detail", article.slug)
        if "dislike" in request.POST:
            article.dislike = F("dislike") + 1
            article.save()
            return redirect("article-detail", article.slug)
        ctx = {
            "article": article,
            "comments": comments,
            "comments_count": comments_count,
            # "form": form,
        }
        return render(request, "niunius/article_detail.html", ctx)


class ShopView(View):
    def get(self, request):
        latest_products = Product.objects.all().order_by("-added")[:6]
        ctx = {
            "latest_products": latest_products,
        }
        return render(request, "niunius/shop.html", ctx)


class CarView(View):
    def get(self, request, slug):
        car = Car.objects.get(slug=slug)
        ctx = {"car": car}
        return render(request, "niunius/car.html", ctx)


class CategoryView(View):
    def get(self, request, slug):
        category = Category.objects.get(slug=slug)
        ctx = {"category": category}
        return render(request, "niunius/category.html", ctx)


class ProductView(View):
    def get(self, request, slug):
        product = Product.objects.get(slug=slug)
        ctx = {"product": product}
        return render(request, "niunius/product.html", ctx)

    def post(self, request, slug):
        product = Product.objects.get(slug=slug)
        qty = int(request.POST.get("qty"))
        if not request.session.get("order"):
            order = Order()
            order.save()
            request.session["order"] = order.id
            OrderItem.objects.create(product=product, quantity=qty, order=order)
            return redirect("cart")
        else:
            order = Order.objects.get(pk=request.session["order"])
            item = order.orderitem_set.filter(product_id=product.pk)
            if item:
                item.quantity += qty
                item.save()
                return redirect("cart")
            else:
                OrderItem.objects.create(product=product, quantity=qty, order=order)
                return redirect("cart")


class DeleteItemView(View):
    def post(self, request, pk):
        item_to_delete = OrderItem.objects.get(pk=pk)
        item_to_delete.delete()
        return redirect("cart")


class ShoppingCartView(View):
    def get(self, request):
        if request.session.get("order"):
            order = Order.objects.get(pk=request.session["order"])
            items = order.orderitem_set.all().order_by("pk")
            total = order.order_total()
            ctx = {
                "items": items,
                "total": total,
            }
            return render(request, "niunius/cart.html", ctx)
        else:
            return render(request, "niunius/cart.html")

    def post(self, request):
        order = Order.objects.get(pk=request.session["order"])
        items = order.orderitem_set.all().order_by("pk")
        qty = int(request.POST.get("qty"))
        product = request.POST.get("product")
        item = order.orderitem_set.get(product=product)
        item.quantity = qty
        item.save()
        total = order.order_total()
        ctx = {
            "items": items,
            "total": total,
        }
        return render(request, "niunius/cart.html", ctx)


class SearchView(ListView):

    template_name = "niunius/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("query")
        queryset = Category.objects.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("query")
        context = super(SearchView, self).get_context_data(**kwargs)
        context["search_product"] = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(code__icontains=query)
        context["search_car"] = Car.objects.filter(model__icontains=query)
        return context


class UserCreationView(View):

    def get(self, request):
        form = UserCreationForm()
        return render(request, "niunius/signup.html", {"form": form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
        else:
            form = UserCreationForm()
        return render(request, "niunius/signup.html", {"form": form})
