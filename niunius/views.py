from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView

import locale
import calendar

from .forms import (
    ArticleForm,
    ArticleCommentForm,
    OrderForm,
    BuyerForm,
    RegisterForm,
    MessageForm,
    VisitForm,
    DeliveryForm,
    PaymentForm,
    GuestForm,
)
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
    CarService,
)


class HomeView(TemplateView):
    """Display the home page - the club logo and the navbar with links leading to subpages."""

    # There is one more thing that may additionally appear on this page. Only the code for it needs to be uncommented.
    # Go through all the files and find it :-)

    template_name = "niunius/base.html"


class RegisterView(CreateView):
    """Create new user."""
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class AboutView(View):
    """Display one specific Article object - information about the club."""

    def get(self, request):
        article = get_object_or_404(Article, slug="o-klubie")
        return render(request, "niunius/about.html", {"article": article})


class ContactView(View):
    """Page with contact details and the message form if users want to contact us."""

    def get(self, request):
        """
        Display the contact page with the map, the address
        and the empty message form.
        """
        form = MessageForm()
        return render(request, "niunius/contact.html", {"form": form})

    def post(self, request):
        """
        If the form is correctly completed, send an e-mail message from the user to the club e-mail address.
        Check my_django_project/settings.py file for email settings.
        """
        form = MessageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["message_name"]
            send_mail(
                name,  # message title
                form.cleaned_data["message"],  # message body
                form.cleaned_data["message_email"],  # from
                ["niunius@niunius.com"],  # to
            )
            form = MessageForm()  # once message sent, clear the form
            return render(request, "niunius/contact.html", {"form": form, "name": name})
        return render(request, "niunius/contact.html", {"form": form})


class CarServiceView(View):
    """Display the table with car services offered by the club."""

    def get(self, request):
        services = CarService.objects.all()
        return render(request, "niunius/car_service.html", {"services": services})


class BookVisitView(View):
    """
    In order to book a visit to the car service station,
    users send their preferences via e-email.
    The site administrator checks if the chosen date and time are available
    and reply to the client.
    """

    def get(self, request):
        """Display the empty visit form."""
        form = VisitForm()
        return render(request, "niunius/book_visit.html", {"form": form})

    def post(self, request):
        """
        If the form is correctly completed,
        then send via e-mail visit details to the club e-mail address.

        Check my_django_project/settings.py file for email settings.
        """
        form = VisitForm(request.POST)
        if form.is_valid():
            client_name = form.cleaned_data["client_name"]
            client_email = form.cleaned_data["client_email"]
            client_phone = form.cleaned_data["client_phone"]
            service = form.cleaned_data["service"].name
            day = form.cleaned_data["visit_date"].day
            month = int(form.cleaned_data["visit_date"].month)
            year = form.cleaned_data["visit_date"].year
            visit_time = form.cleaned_data["visit_time"]

            locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
            visit_date = f"{day} {calendar.month_name[month]} {year}"

            msg_title = f"{client_name} - {service}"
            msg_body = (
                f"{client_name}, tel. {client_phone}, usługa: {service},"
                f" dzień: {visit_date}, czas: {visit_time}"
            )
            send_mail(
                msg_title,  # message title
                msg_body,  # message body
                client_email,  # from
                ["niunius@niunius.com"],  # to
            )
            form = VisitForm()  # once message sent, clear the form
            ctx = {
                "form": form,
                "client_name": client_name,
                "client_email": client_email,
                "client_phone": client_phone,
                "service": service,
                "visit_date": visit_date,
                "visit_time": visit_time,
            }
            return render(request, "niunius/book_visit.html", ctx)
        return render(request, "niunius/book_visit.html", {"form": form})


class BlogView(View):
    """
    Get the list of articles, excluding the article displayed in the AboutView.
    The page is divided in two parts.
    The part on the left shows the list of articles titles,
    sorted by the date on which added, from the newest to the oldest ones,
    not more than 10 articles per one page.
    The part on the right displays on the carousel photos of the three latest articles.
    """

    def get(self, request):
        articles = Article.objects.exclude(slug="o-klubie").order_by("-added")
        paginator = Paginator(articles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        carousel_articles = articles[:4]
        ctx = {
            "articles": articles,
            "page_obj": page_obj,
            "carousel_articles": carousel_articles,
        }
        return render(request, "niunius/blog.html", ctx)


class AddArticleView(LoginRequiredMixin, View):
    """Add a new article to the blog page. Only for logged users."""

    login_url = reverse_lazy("login")

    def get(self, request):
        """Display the empty article form."""
        form = ArticleForm()
        return render(request, "niunius/article_form.html", {"form": form})

    def post(self, request):
        """
        If the form is correctly completed
        (title and content fields are required, photos optional),
        create new Article object
        and related to it ArticlePhoto objects (if any photos added in the form).
        """
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            article = Article.objects.create(
                title=title, content=content, added_by=request.user
            )
            for photo in request.FILES.getlist("photos"):
                ArticlePhoto.objects.create(photo=photo, article=article)
            return redirect("blog")
        return render(request, "niunius/article_form.html", {"form": form})


class UpdateArticleView(LoginRequiredMixin, View):
    """
    Edit a given article. Only for logged users.
    User who want to edit the article may be different from the user who has created this article.
    """

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        """Display the article form with fields filled in with the details of the given article."""
        article = get_object_or_404(Article, pk=pk)
        form = ArticleForm({"title": article.title, "content": article.content})
        ctx = {"article": article, "form": form}
        return render(request, "niunius/article_update.html", ctx)

    def post(self, request, pk):
        """Save changes to the given article."""
        form = ArticleForm(request.POST, request.FILES)
        article = get_object_or_404(Article, pk=pk)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            article.title = title
            article.content = content
            article.updated_by = request.user
            article.save()
            for photo in request.FILES.getlist("photos"):
                ArticlePhoto.objects.create(photo=photo, article=article)
            return redirect("article-detail", article.slug)
        return render(request, "niunius/article_update.html", {"form": form})


class ArticleDetailView(View):
    """
    Page with the article details and with functionalities to add comments, like or dislike the article.
    Any user can click 'like' and 'dislike' buttons. Adding comments only for logged in users.
    """

    def get(self, request, slug):
        """Display details of the given article."""
        article = get_object_or_404(Article, slug=slug)
        comments = article.articlecomment_set.all().order_by("-added")
        ctx = {
            "article": article,
            "comments": comments,
            "comments_count": comments.count(),
            "form": ArticleCommentForm(),
        }
        return render(request, "niunius/article_detail.html", ctx)

    def post(self, request, slug):
        """If new values provided, update 'like' or 'dislike' numbers of the given article."""
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


class AddCommentView(LoginRequiredMixin, View):
    """Add a comment to the given article. Only for logged users."""

    login_url = reverse_lazy("login")

    def get(self, request, pk):
        """Display the empty comment form."""
        ctx = {
            "article": get_object_or_404(Article, pk=pk),
            "form": ArticleCommentForm(),
        }
        return render(request, "niunius/article_comment_form.html", ctx)

    def post(self, request, pk):
        """If the form is correctly completed, create new ArticleComment object."""
        form = ArticleCommentForm(request.POST)
        article = get_object_or_404(Article, pk=pk)
        if form.is_valid():
            text = form.cleaned_data["text"]
            ArticleComment.objects.create(article=article, text=text, user=request.user)
            return redirect("article-detail", article.slug)
        return redirect("add-comment", {"form": form, "article": article})


class ShopView(View):
    """
    List categories and car models on the left sidebar.
    Also display images of products recently added to the store.
    Skip products with stock equal to 0.
    """

    def get(self, request):
        latest_products = Product.objects.exclude(stock=0).order_by("-added")[:6]
        return render(
            request, "niunius/shop.html", {"latest_products": latest_products}
        )


class SearchView(ListView):
    """
    Search for given query among Category names, Product names and codes, and Car models.
    Display the results.
    As for products in the results, show only available ones, skip those with stock equal to 0.
    """

    template_name = "niunius/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("query")
        queryset = Category.objects.filter(name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("query")
        context = super(SearchView, self).get_context_data(**kwargs)
        products = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(code__icontains=query)
        context["search_product"] = products.exclude(stock=0)
        context["search_car"] = Car.objects.filter(model__icontains=query)
        return context


class CarView(View):
    """
    Display details of the given car.
    As for products related to the car, show only available ones, skip those with stock equal to 0.
    """

    def get(self, request, slug):
        car = get_object_or_404(Car, slug=slug)
        ctx = {"car": car}
        return render(request, "niunius/car.html", ctx)


class CategoryView(View):
    """
    Display details of the given category.
    As for products related to the car, show only available ones, skip those with stock equal to 0.
    """

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug)
        ctx = {"category": category}
        return render(request, "niunius/category.html", ctx)


class ProductView(View):
    """Product details page with functionality of adding the product to the shopping cart."""

    def get(self, request, slug):
        """Display details of the given product."""
        product = get_object_or_404(Product, slug=slug)
        return render(request, "niunius/product.html", {"product": product})

    def post(self, request, slug):
        """
        All users can add the product to the shopping cart.
        However, it is handled differently for logged and not logged in users.

        For anonymous users, the given shopping cart is available and editable only in the session.
        For logged users, once the shopping cart is created (creation is when the first item is added to the cart),
        the cart is saved and is editable at any time, if the user logged in, till the order is placed.
        """
        product = Product.objects.get(slug=slug)
        qty = int(request.POST.get("qty"))

        if request.user.is_authenticated:
            try:
                cart = ShoppingCart.objects.get(is_ordered=False)
            except ShoppingCart.DoesNotExist:
                new_cart = ShoppingCart.objects.create(is_ordered=False)
                CartItem.objects.create(product=product, quantity=qty, cart=new_cart)
                return redirect("shopping-cart")
            try:
                item = cart.cartitem_set.get(product_id=product.pk)
            except CartItem.DoesNotExist:
                CartItem.objects.create(product=product, quantity=qty, cart=cart)
                return redirect("shopping-cart")

        else:
            if "cart" not in request.session:
                new_cart = ShoppingCart.objects.create()
                request.session["cart"] = new_cart.id
                CartItem.objects.create(product=product, quantity=qty, cart=new_cart)
                return redirect("shopping-cart")
            else:
                cart = ShoppingCart.objects.get(pk=request.session["cart"])
                try:
                    item = cart.cartitem_set.get(product_id=product.pk)
                except CartItem.DoesNotExist:
                    CartItem.objects.create(product=product, quantity=qty, cart=cart)
                    return redirect("shopping-cart")

        item.quantity += qty
        item.save()
        cart.cartitem_set.get(product_id=product.pk).quantity += qty
        cart.cartitem_set.get(product_id=product.pk).save()
        return redirect("shopping-cart")


class ShoppingCartView(View):
    """
    Shopping cart with added items.
    Previously chosen item quantity may be changed in this view and all values will be recalculated accordingly.

    For anonymous users, the given shopping cart is available and editable only in the session.
    For logged users, once the shopping cart is created (creation is when the first item is added to the cart),
    the cart is saved and is editable at any time, if the user logged in, till the order is placed.
    """

    def get(self, request):
        """Display the shopping cart with all added items."""
        try:
            if request.user.is_authenticated:
                cart = ShoppingCart.objects.get(is_ordered=False)
            else:
                cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
        except ShoppingCart.DoesNotExist:
            return render(request, "niunius/shopping_cart.html")
        items = cart.cartitem_set.all().order_by("pk")
        total = cart.total()
        ctx = {"items": items, "total": total}
        return render(request, "niunius/shopping_cart.html", ctx)

    def post(self, request):
        """
        If the quantity is changed for a given cart item,
        recalculate the item value and the total value of the cart accordingly.
        """
        if request.user.is_authenticated:
            cart = ShoppingCart.objects.get(is_ordered=False)
        else:
            cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
        items = cart.cartitem_set.all().order_by("pk")
        qty = int(request.POST.get("qty"))
        product = request.POST.get("product")
        item = cart.cartitem_set.get(product=product)
        item.quantity = qty
        item.save()
        total = cart.total()
        ctx = {"items": items, "total": total}
        return render(request, "niunius/shopping_cart.html", ctx)


class DeleteItemView(View):
    """Delete the given cart item from the shopping cart."""

    def post(self, request, pk):
        item_to_delete = CartItem.objects.get(pk=pk)
        item_to_delete.delete()
        return redirect("shopping-cart")


class OrderView(View):
    """
    Order view for logged users.

    For logged users, once the shopping cart is created (creation is when the first item is added to the cart),
    the cart is saved and is editable at any time, if the user logged in, till the order is placed.
    """

    def get(self, request):
        """
        Display the order forms for buyers who have accounts and are logged in..
        Fill them with the personal and address data (if available) of the logged user.
        """
        form = (
            OrderForm(
                initial={
                    "address_country": request.user.order_set.latest(
                        "pk"
                    ).address_country,
                    "address_street": request.user.order_set.latest(
                        "pk"
                    ).address_street,
                    "address_zipcode": request.user.order_set.latest(
                        "pk"
                    ).address_zipcode,
                    "address_city": request.user.order_set.latest("pk").address_city,
                }
            )
            if request.user.order_set.all()
            else OrderForm()
        )
        buyer_form = BuyerForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            }
        )
        delivery_form = DeliveryForm()
        payment_form = PaymentForm()
        ctx = {
            "form": form,
            "buyer_form": buyer_form,
            "delivery_form": delivery_form,
            "payment_form": payment_form,
        }
        return render(request, "niunius/order_form.html", ctx)

    def post(self, request):
        """Save the order with provided details."""
        form = OrderForm(request.POST)
        buyer_form = BuyerForm(request.POST)
        delivery_form = DeliveryForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if (
            form.is_valid()
            and buyer_form.is_valid()
            and delivery_form.is_valid()
            and payment_form.is_valid()
        ):
            address_city = form.cleaned_data["address_city"]
            address_zipcode = form.cleaned_data["address_zipcode"]
            address_street = form.cleaned_data["address_street"]
            address_country = form.cleaned_data["address_country"]
            delivery_method = delivery_form.cleaned_data["delivery_method"]
            payment_method = payment_form.cleaned_data["payment_method"]
            cart = ShoppingCart.objects.get(is_ordered=False)
            try:
                order = Order.objects.get(cart_id=cart.id)
            except Order.DoesNotExist:
                order = Order.objects.create(
                    cart=cart,
                    buyer=request.user,
                    address_city=address_city,
                    address_zipcode=address_zipcode,
                    address_street=address_street,
                    address_country=address_country,
                    delivery=delivery_method,
                    payment=payment_method,
                )
            order.address_city = address_city
            order.address_zipcode = address_zipcode
            order.address_street = address_street
            order.address_country = address_country
            order.delivery = delivery_method
            order.payment = payment_method
            order.save()

            buyer = request.user
            buyer.first_name = buyer_form.cleaned_data["first_name"]
            buyer.last_name = buyer_form.cleaned_data["last_name"]
            buyer.email = buyer_form.cleaned_data["email"]
            buyer.save()

            return redirect("confirm-order", order.pk)

        ctx = {
            "form": form,
            "buyer_form": buyer_form,
            "delivery_form": delivery_form,
            "payment_form": payment_form,
        }
        return render(request, "niunius/order_form.html", ctx)


class GuestOrderView(View):
    """
    Order view for anonymous users.
    For anonymous users, the given shopping cart is available and editable only in the session.
    """

    def get(self, request):
        """Display the order forms for guest buyers."""
        form = OrderForm()
        guest_form = GuestForm()
        delivery_form = DeliveryForm()
        payment_form = PaymentForm()
        ctx = {
            "form": form,
            "guest_form": guest_form,
            "delivery_form": delivery_form,
            "payment_form": payment_form,
        }
        return render(request, "niunius/guest_order_form.html", ctx)

    def post(self, request):
        """Save the order with provided details."""
        form = OrderForm(request.POST)
        guest_form = GuestForm(request.POST)
        delivery_form = DeliveryForm(request.POST)
        payment_form = PaymentForm(request.POST)
        if (
            form.is_valid()
            and guest_form.is_valid()
            and delivery_form.is_valid()
            and payment_form.is_valid()
        ):
            address_city = form.cleaned_data["address_city"]
            address_zipcode = form.cleaned_data["address_zipcode"]
            address_street = form.cleaned_data["address_street"]
            address_country = form.cleaned_data["address_country"]
            delivery_method = delivery_form.cleaned_data["delivery_method"]
            payment_method = payment_form.cleaned_data["payment_method"]
            cart = ShoppingCart.objects.get(pk=request.session.get("cart"))
            try:
                order = Order.objects.get(cart_id=cart.id)
            except Order.DoesNotExist:
                order = Order.objects.create(
                    cart=cart,
                    address_city=address_city,
                    address_zipcode=address_zipcode,
                    address_street=address_street,
                    address_country=address_country,
                    delivery=delivery_method,
                    payment=payment_method,
                )
            order.address_city = address_city
            order.address_zipcode = address_zipcode
            order.address_street = address_street
            order.address_country = address_country
            order.delivery = delivery_method
            order.payment = payment_method
            order.save()

            order.guest_buyer_first_name = guest_form.cleaned_data["guest_first_name"]
            order.guest_buyer_last_name = guest_form.cleaned_data["guest_last_name"]
            order.guest_buyer_email = guest_form.cleaned_data["guest_email"]
            order.save()

            return redirect("confirm-order", order.pk)

        ctx = {
            "form": form,
            "guest_form": guest_form,
            "delivery_form": delivery_form,
            "payment_form": payment_form,
        }
        return render(request, "niunius/guest_order_form.html", ctx)


class OrderConfirmationView(View):
    """
    Display order details so as the user may confirm and proceed
    or return to the previous page and edit if needed.
    """

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        items = order.cart.cartitem_set.all().order_by("pk")
        ctx = {"order": order, "items": items}
        return render(request, "niunius/order_confirmation.html", ctx)


class PurchaseView(View):
    """
    Display the message confirming the purchase..
    Decrease the stock with the ordered quantities.
    Set the shopping cart related to this order to is_ordered = True for logged users
    or delete it from the session for anonymous users.
    """

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        for item in order.cart.cartitem_set.all():
            item.product.stock -= item.quantity
            item.product.save()
        order.cart.is_ordered = True
        if "cart" in request.session:
            del request.session["cart"]
        order.cart.save()
        order.save()
        return render(request, "niunius/purchase.html")
