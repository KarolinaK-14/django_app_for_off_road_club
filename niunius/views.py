from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.views import View
from django.views.generic import ListView, TemplateView

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
    """Display the home page."""

    template_name = "niunius/base.html"


class LogoutView(View):
    """Log out the user and redirect directly to the home page."""

    def get(self, request):
        logout(request)
        return redirect("home")


class RegisterView(View):
    """
    Display the user creation form.
    If the form filled out correctly, create, authenticate and log in the new user.
    """

    def get(self, request):
        form = RegisterForm()
        return render(request, "niunius/register_form.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            raw_password = form.cleaned_data["password1"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            user = User.objects.create_user(
                username=username,
                password=raw_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            authenticate(user)
            login(request, user)
            next_url = request.GET.get("next")
            if not next_url or next_url == "/accounts/login/":
                return redirect("home")
            return redirect(next_url)

        return render(request, "niunius/register_form.html", {"form": form})


class ContactView(View):
    """
    Display the contact page with the message form.
    The form is for sending an email message.
    Check my_django_project/settings.py file for email settings.
    """

    def get(self, request):
        form = MessageForm()
        return render(request, "niunius/contact.html", {"form": form})

    def post(self, request):
        form = MessageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["message_name"]
            send_mail(
                name,  # message title
                form.cleaned_data["message"],  # message body
                form.cleaned_data["message_email"],  # from
                ["niunius@niunius.com"],  # to
            )
            form = MessageForm()
            return render(request, "niunius/contact.html", {"form": form, "name": name})
        return render(request, "niunius/contact.html", {"form": form})


class CarServiceView(View):
    """
    Display the list of services with details.
    And the button linked to the page with the form to book the visit.
    """

    def get(self, request):
        services = CarService.objects.all()
        return render(request, "niunius/car_service.html", {"services": services})


class BookVisitView(View):
    """
    Display the form to book a visit.
    Booking means sending an email.
    Check my_django_project/settings.py file for email settings.
    """

    def get(self, request):
        form = VisitForm()
        return render(request, "niunius/book_visit.html", {"form": form})

    def post(self, request):
        form = VisitForm(request.POST)
        if form.is_valid():
            client_name = form.cleaned_data["client_name"]
            client_email = form.cleaned_data["client_email"]
            client_phone = form.cleaned_data["client_phone"]
            service = form.cleaned_data["service"].name
            day = int(form.cleaned_data["visit_date"].day)
            month = int(form.cleaned_data["visit_date"].month)
            year = int(form.cleaned_data["visit_date"].year)
            locale.setlocale(locale.LC_ALL, "pl_PL.utf8")
            visit_date = f"{day} {calendar.month_name[month]} {year}"
            visit_time = form.cleaned_data["visit_time"]
            msg_title = f"{client_name} - {service}"
            msg_body = f"{client_name}, tel. {client_phone}, usługa: {service}, dzień: {visit_date}, czas: {visit_time}"
            send_mail(
                msg_title,  # message title
                msg_body,  # message body
                client_email,  # from
                ["niunius@niunius.com"],  # to
            )
            form = VisitForm()
            return render(
                request,
                "niunius/book_visit.html",
                {
                    "form": form,
                    "client_name": client_name,
                    "client_email": client_email,
                    "client_phone": client_phone,
                    "service": service,
                    "visit_date": visit_date,
                    "visit_time": visit_time,
                },
            )
        return render(request, "niunius/book_visit.html", {"form": form})


class AboutView(View):
    def get(self, request):
        article = Article.objects.get(slug="o-klubie")
        return render(request, "niunius/about.html", {"article": article})


class BlogView(View):
    """
    Get the list of articles,
    sorted by the date on which added, from the newest to the oldest ones.
    Display not more than 10 articles per one page.
    """

    def get(self, request):
        articles = Article.objects.exclude(title="o-klubie").order_by("-added")
        paginator = Paginator(articles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        ctx = {"articles": articles, "page_obj": page_obj}
        return render(request, "niunius/blog.html", ctx)


class AddArticleView(LoginRequiredMixin, View):
    """
    Give access only to logged in users.
    If a user is not logged in redirect to the login page.
    """

    login_url = reverse_lazy("login")

    def get(self, request):
        """Display the empty form for adding a new article."""
        form = ArticleForm()
        return render(request, "niunius/article_form.html", {"form": form})

    def post(self, request):
        """
        Add to the database new Article object and related to it ArticlePhoto objects.
        If added successfully, redirect to the main blog page.
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
    login_url = reverse_lazy("login")

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        ctx = {
            "article": article,
            "form": ArticleForm({"title": article.title, "content": article.content}),
        }
        return render(request, "niunius/article_update.html", ctx)

    def post(self, request, pk):
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


class AddCommentView(LoginRequiredMixin, View):
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
        ctx = {
            "article": get_object_or_404(Article, pk=pk),
            "form": ArticleCommentForm(),
        }
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
        return redirect("add-comment", {"form": form, "article": article})


class ArticleDetailView(View):
    def get(self, request, slug):
        """Get details of the given article."""
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
        ctx = {
            "latest_products": Product.objects.exclude(stock=0).order_by("-added")[:6]
        }
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
        product = get_object_or_404(Product, slug=slug)
        ctx = {"product": product}
        return render(request, "niunius/product.html", ctx)

    def post(self, request, slug):
        product = Product.objects.get(slug=slug)
        qty = int(request.POST.get("qty"))
        try:
            cart = ShoppingCart.objects.get(is_ordered=False)
        except ShoppingCart.DoesNotExist:
            new_cart = ShoppingCart.objects.create()
            CartItem.objects.create(product=product, quantity=qty, cart=new_cart)
            return redirect("shopping-cart")

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


class DeleteItemView(View):
    def post(self, request, pk):
        """Delete the given item from the shopping cart."""
        item_to_delete = CartItem.objects.get(pk=pk)
        item_to_delete.delete()
        return redirect("shopping-cart")


class ShoppingCartView(View):
    def get(self, request):
        try:
            cart = ShoppingCart.objects.get(is_ordered=False)
        except ShoppingCart.DoesNotExist:
            return render(request, "niunius/shopping_cart.html")
        items = cart.cartitem_set.all().order_by("pk")
        total = cart.total()
        ctx = {"items": items, "total": total}
        return render(request, "niunius/shopping_cart.html", ctx)

    def post(self, request):
        cart = ShoppingCart.objects.get(is_ordered=False)
        items = cart.cartitem_set.all().order_by("pk")
        qty = int(request.POST.get("qty"))
        product = request.POST.get("product")
        item = cart.cartitem_set.get(product=product)
        item.quantity = qty
        item.save()
        total = cart.total()
        ctx = {"items": items, "total": total}
        return render(request, "niunius/shopping_cart.html", ctx)


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


class OrderView(View):
    def get(self, request):

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
        delivery_form = DeliveryForm(initial={"delivery_method": "Kurier"})
        payment_form = PaymentForm(initial={"payment_method": "Przelew"})
        return render(
            request,
            "niunius/order_form.html",
            {
                "form": form,
                "buyer_form": buyer_form,
                "delivery_form": delivery_form,
                "payment_form": payment_form,
            },
        )

    def post(self, request):

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
        return render(
            request,
            "niunius/order_form.html",
            {
                "form": form,
                "buyer_form": buyer_form,
                "delivery_form": delivery_form,
                "payment_form": payment_form,
            },
        )


class GuestOrderView(View):
    def get(self, request):
        form = OrderForm()
        guest_form = GuestForm()
        delivery_form = DeliveryForm(initial={"delivery_method": "Kurier"})
        payment_form = PaymentForm(initial={"payment_method": "Przelew"})
        return render(
            request,
            "niunius/guest_order_form.html",
            {
                "form": form,
                "guest_form": guest_form,
                "delivery_form": delivery_form,
                "payment_form": payment_form,
            },
        )

    def post(self, request):
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
            cart = ShoppingCart.objects.get(is_ordered=False)
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
        return render(
            request,
            "niunius/guest_order_form.html",
            {
                "form": form,
                "guest_form": guest_form,
                "delivery_form": delivery_form,
                "payment_form": payment_form,
            },
        )


class OrderConfirmationView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        items = order.cart.cartitem_set.all().order_by("pk")
        ctx = {"order": order, "items": items}
        return render(request, "niunius/order_confirmation.html", ctx)


class PurchaseView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        for item in order.cart.cartitem_set.all():
            item.product.stock -= item.quantity
            item.product.save()
        order.cart.is_ordered = True
        order.cart.save()
        order.save()
        return render(request, "niunius/purchase.html")
