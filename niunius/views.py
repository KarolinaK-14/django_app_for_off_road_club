from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView
from .forms import ArticleForm, ArticleCommentForm, OrderForm, BuyerForm
from .models import (
    Article,
    ArticlePhoto,
    ArticleComment,
    Car,
    Category,
    Product,
    ShoppingCart,
    CartItem,
    Order,
)


class HomeView(TemplateView):
    """Render the base.html file."""

    template_name = "niunius/base.html"


class BlogView(View):
    def get(self, request):
        """
        Get the list of articles,
        sorted by the date on which added, from the newest to the oldest ones.
        Display not more than 10 articles per one page.
        """
        articles = Article.objects.all().order_by("-added")
        paginator = Paginator(articles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        ctx = {"articles": articles, "page_obj": page_obj}
        return render(request, "niunius/blog.html", ctx)


class ArticleAddView(LoginRequiredMixin, View):
    """
    Give access only to logged in users.
    If a user is not logged in redirect to the login page.
    """

    login_url = reverse_lazy("login")

    def get(self, request):
        """Return the page with an empty form for adding a new article."""
        form = ArticleForm()
        ctx = {"form": form}
        return render(request, "niunius/article_form.html", ctx)

    def post(self, request):
        """
        Add to the database new Article object and related to it ArticlePhoto objects.
        If added successfully, redirect to the ain blog page.
        Otherwise, return the page with an empty form.
        """
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


class CommentAddView(LoginRequiredMixin, View):
    """
    Give access only to logged in users.
    If a user is not logged in redirect to the login page.
    """

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        """
        Return the page with an empty form
        for adding a new comment to the given article.
        """
        article = get_object_or_404(Article, pk=pk)
        form = ArticleCommentForm()
        ctx = {"form": form, "article": article}
        return render(request, "niunius/article_comment_form.html", ctx)

    def post(self, request, pk):
        """
        Add to the given article new ArticleComment object.
        If added successfully, redirect to the page with article details.
        Otherwise, return the page with an empty form.
        """
        form = ArticleCommentForm(request.POST)
        article = get_object_or_404(Article, pk=pk)
        if form.is_valid():
            text = form.cleaned_data["text"]
            ArticleComment.objects.create(article=article, text=text, user=request.user)
            return redirect("article-detail", article.slug)
        ctx = {"form": form, "article": article}
        return redirect("add-comment", ctx)


class ArticleDetailView(View):
    def get(self, request, slug):
        """Get details of the given article."""
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
        """
        If new values given,
        update 'like' or 'dislike' field of the given Article object.
        """
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
        }
        return render(request, "niunius/article_detail.html", ctx)


class ShopView(View):
    def get(self, request):
        """
        Get the list of products,
        sorted by the date on which added, from the newest to the oldest ones.
        Display not more than first six items from the list.
        """
        latest_products = Product.objects.all().order_by("-added")[:6]
        ctx = {"latest_products": latest_products}
        return render(request, "niunius/shop.html", ctx)


class CarView(View):
    def get(self, request, slug):
        """Get details of the given car."""
        car = get_object_or_404(Car, slug=slug)
        ctx = {"car": car}
        return render(request, "niunius/car.html", ctx)


class CategoryView(View):
    def get(self, request, slug):
        """Get details of the given category."""
        category = get_object_or_404(Category, slug=slug)
        ctx = {"category": category}
        return render(request, "niunius/category.html", ctx)


class ProductView(View):
    def get(self, request, slug):
        """Get details of the given product."""
        product = Product.objects.get(slug=slug)
        ctx = {"product": product}
        return render(request, "niunius/product.html", ctx)

    def post(self, request, slug):
        """
        If no shopping cart in the session, create and save one.
        Then add to the cart the product with the chosen quantity.

        If a shopping cart already saved in the session,
        just add the product with the chosen quantity.

        If the product already added to the cart, just update its quantity.
        """
        product = Product.objects.get(slug=slug)
        qty = int(request.POST.get("qty"))
        if "cart" not in request.session:
            cart = ShoppingCart.objects.create()
            request.session["cart"] = cart.id
            CartItem.objects.create(product=product, quantity=qty, cart=cart)
            return redirect("cart")
        else:
            cart = ShoppingCart.objects.get(pk=request.session["cart"])
            try:
                item = cart.cartitem_set.get(product_id=product.pk)
            except CartItem.DoesNotExist:
                CartItem.objects.create(product=product, quantity=qty, cart=cart)
                return redirect("cart")
            item.quantity += qty
            item.save()
            cart.cartitem_set.get(product_id=product.pk).quantity += qty
            cart.cartitem_set.get(product_id=product.pk).save()
            return redirect("cart")


class DeleteItemView(View):
    def post(self, request, pk):
        """Delete the given item from the shopping cart."""
        item_to_delete = CartItem.objects.get(pk=pk)
        item_to_delete.delete()
        return redirect("cart")


class ShoppingCartView(View):
    def get(self, request):
        """
        Get items from the shopping cart saved in the session.
        Calculate the total value of these items (quantity * price).

        If no shopping cart saved, display the message about empty cart.
        """
        if request.session.get("cart"):
            cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
            items = cart.cartitem_set.all().order_by("pk")
            total = cart.order_total()
            ctx = {"items": items, "total": total}
            return render(request, "niunius/cart.html", ctx)
        else:
            return render(request, "niunius/cart.html")

    def post(self, request):
        """
        Update quantity for given item
        and re-calculate the total value of all items in the cart.
        """
        cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
        items = cart.cartitem_set.all().order_by("pk")
        qty = int(request.POST.get("qty"))
        product = request.POST.get("product")
        item = cart.cartitem_set.get(product=product)
        item.quantity = qty
        item.save()
        total = cart.order_total()
        ctx = {"items": items, "total": total}
        return render(request, "niunius/cart.html", ctx)


class SearchView(ListView):
    """
    Search for given query among Category names,
    Product names and codes, and Car models.
    Display the results.
    """

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
        """Return the page with an empty form for adding a new user."""
        form = UserCreationForm()
        return render(request, "niunius/signup.html", {"form": form})

    def post(self, request):
        """
        Add to the database new User object.
        If added successfully, authenticate the new user, log the user in,
        and redirect to the home page.
        Otherwise, return the page with an empty form.
        """
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            raw_password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("home")
        return render(request, "niunius/signup.html", {"form": form})


class OrderView(LoginRequiredMixin, View):
    """
    Give access only to logged in users.
    If a user is not logged in redirect to the login page.
    """

    login_url = reverse_lazy("login")

    def get(self, request):
        """Return the page with an empty form for creating a new order."""
        form = OrderForm()
        buyer_form = BuyerForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            }
        )
        return render(
            request, "niunius/order_form.html", {"form": form, "buyer_form": buyer_form}
        )

    def post(self, request):
        """
        Add to the database new Order object.
        If added successfully, redirect to the confirmation page.
        Otherwise, return the page with an empty form.

        After the order is created, delete the assigned cart from the session
        and decrease the stock field for ordered products.
        """
        form = OrderForm(request.POST)
        buyer_form = BuyerForm(request.POST)
        if form.is_valid() and buyer_form.is_valid():
            address_city = form.cleaned_data["address_city"]
            address_zipcode = form.cleaned_data["address_zipcode"]
            address_street = form.cleaned_data["address_street"]
            address_country = form.cleaned_data["address_country"]
            cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
            order = Order.objects.create(
                cart=cart,
                buyer=request.user,
                address_city=address_city,
                address_zipcode=address_zipcode,
                address_street=address_street,
                address_country=address_country,
            )
            buyer = request.user
            buyer.first_name = buyer_form.cleaned_data["first_name"]
            buyer.last_name = buyer_form.cleaned_data["last_name"]
            buyer.email = buyer_form.cleaned_data["email"]
            buyer.save()
            for item in cart.cartitem_set.all():
                item.product.stock -= item.quantity
                item.product.save()
            del request.session["cart"]
            return redirect("confirmation", order.pk)
        return render(
            request, "niunius/order_form.html", {"form": form, "buyer_form": buyer_form}
        )


class ConfirmationView(View):
    def get(self, request, pk):
        """Return the confirmation of the given order,
        including the payment instruction."""
        order = Order.objects.get(pk=pk)
        items = order.cart.cartitem_set.all().order_by("pk")
        payment_msg = (
            f"Dziękujemy za złożenie zamówienia w naszym sklepie. "
            f"Aby sfinalizować zakup wykonaj przelew na konto bankowe nr: 1234567890. "
            f'W tytule przelewu wpisz: "{order.buyer.first_name} {order.buyer.last_name}, '
            f'zamówienie #{order.pk}, '
            f'{timezone.now().date()}"'
        )

        ctx = {"order": order, "items": items, "payment_msg": payment_msg}
        return render(request, "niunius/confirmation.html", ctx)
