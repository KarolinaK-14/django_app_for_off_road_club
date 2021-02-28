from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    """
    Title: title of the article
    Slug: slugified title
    Content: content of the article
    Added_by: user who created the article, User object
    Updated_by: user who made some changes, User object;
    user editing the article may be different from user who has created this article
    Added: date & time of creation
    Updated: date & time of update
    Like: how many times users pressed 'like' button for the article, default = 0
    Dislike: how many times users pressed 'dislike' button for the article, default = 0
    """

    title = models.CharField(max_length=128, verbose_name="Tytuł")
    slug = models.SlugField(unique=True, blank=True, max_length=128)
    content = models.TextField(verbose_name="Treść")
    added_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Dodane przez",
        related_name="creation",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Zmienione przez",
        null=True,
        blank=True,
        related_name="update",
    )
    added = models.DateTimeField(auto_now_add=True, verbose_name="Dodano")
    updated = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Zmieniono"
    )
    like = models.IntegerField(default=0, verbose_name="Lubię")
    dislike = models.IntegerField(default=0, verbose_name="Nie lubię")

    class Meta:
        verbose_name = "Artykuł"
        verbose_name_plural = "Artykuły"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class ArticlePhoto(models.Model):
    """
    Article: Article object; each article can have many photos
    Photo: photo of the article
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, verbose_name="Artykuł"
    )
    photo = models.ImageField(upload_to="niunius/blog_img", verbose_name="Zdjęcie")

    class Meta:
        verbose_name = "Artykuł-zdjęcie"
        verbose_name_plural = "Artykuł-zdjęcia"

    def __str__(self):
        return self.photo.name


class ArticleComment(models.Model):
    """
    Article: Article object
    Text: text of the comment
    User: who has added the comment, User object
    Added: when the comment was added
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, verbose_name="Artykuł"
    )
    text = models.TextField(verbose_name="Tekst")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Użytkownik")
    added = models.DateTimeField(auto_now_add=True, verbose_name="Dodano")

    class Meta:
        verbose_name = "Artykuł-komentarz"
        verbose_name_plural = "Artykuł-komentarze"

    def __str__(self):
        return f"komentarz dodany {self.added} przez {self.user}"


class Car(models.Model):
    """
    Brand: brand of the car
    Model: model of the car brand, unique
    Slug: slugified name of the car; name is a concatenation of car brand and car model
    Image: image of the car
    """

    brand = models.CharField(max_length=64, verbose_name="Marka")
    model = models.CharField(max_length=64, unique=True, verbose_name="Model")
    slug = models.SlugField(unique=True, blank=True, max_length=128)
    image = models.ImageField(
        blank=True, upload_to="niunius/car_img/", verbose_name="Zdjęcie"
    )

    @property
    def name(self):
        return f"{self.brand} {self.model}"

    class Meta:
        verbose_name = "Auta"
        verbose_name_plural = "Auto"

    def __str__(self):
        return self.name

    def get_available_products(self):
        """Display only these products related to the car for which stock is not equal to 0."""
        return self.product_set.exclude(stock=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Car, self).save(*args, **kwargs)


class Category(models.Model):
    """
    Name: name of the category
    Slug: slugified name of the category
    """

    name = models.CharField(max_length=64, verbose_name="Nazwa")
    slug = models.SlugField(unique=True, blank=True, max_length=64)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name

    def get_available_products(self):
        """Display only these products related to the category for which stock is not equal to 0."""
        return self.product_set.exclude(stock=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    """
    Name: name of the product
    Slug: slugified name of the product
    Added: when the product was added
    Code: unique code of the product
    Stock: available quantity of the product
    Description: description of the product
    Price: price of the product
    Image: image of the product
    Cars: set of Car objects to which the product is related
    Categories: set of Category objects to which the product is related
    """

    name = models.CharField(max_length=128, verbose_name="Nazwa")
    slug = models.SlugField(unique=True, blank=True, max_length=128)
    added = models.DateTimeField(auto_now_add=True, verbose_name="Dodano")
    code = models.CharField(max_length=128, unique=True, verbose_name="Kod produktu")
    stock = models.IntegerField(
        validators=[MinValueValidator(0)], verbose_name="Dostępność"
    )
    description = models.TextField(verbose_name="Opis")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Cena")
    image = models.ImageField(
        blank=True, upload_to="niunius/product_img/", verbose_name="Zdjęcie"
    )
    cars = models.ManyToManyField(Car, verbose_name="Pasuje do auta")
    categories = models.ManyToManyField(Category, verbose_name="Należy do kategorii")

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


class ShoppingCart(models.Model):
    """
    Is_ordered:
        False - when the shopping cart is created for logged users
        True - when the order related to the shopping cart is finalized, only for logged users
        Null - for anonymous users
    """

    is_ordered = models.BooleanField(null=True)

    class Meta:
        verbose_name = "Koszyk"
        verbose_name_plural = "Koszyki"

    def total(self):
        """Calculate the total value of the shopping cart, amount to pay."""
        return sum([item.value for item in self.cartitem_set.all()])

    def __str__(self):
        return f"Koszyk nr: {self.id}"


class CartItem(models.Model):
    """
    Product: related Product object
    Quantity: quantity of a given product in a given shopping cart
    Cart: related ShoppingCart object
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Produkt"
    )
    quantity = models.IntegerField(
        verbose_name="Ilość", validators=[MinValueValidator(0)]
    )
    cart = models.ForeignKey(
        ShoppingCart, on_delete=models.CASCADE, verbose_name="Koszyk"
    )

    @property
    def value(self):
        return self.quantity * self.product.price

    class Meta:
        verbose_name = "W koszyku"
        verbose_name_plural = "W koszyku"

    def __str__(self):
        return f"{self.product.name}, {self.quantity} szt., nr koszyka: {self.cart.id}"


class Order(models.Model):
    """
    Cart: related ShoppingCart object
    Buyer: logged user who placed the order, can be null as orders by guests are allowed
    Guest_buyer_first_name:
        the first name of the buyer-guest who placed the order, can be null if buyer-logged user exists
    Guest_buyer_last_name:
        the last name of the buyer-guest who placed the order, can be null if buyer-logged user exists
    Guest_buyer_email:
        the e-mail the buyer-guest who placed the order, can be null if buyer-logged user exists
    Address_city, Address_zipcode, Address_street, Address_country:
        details for the address of the buyer who placed the order
    Date: date & time of the order
    Delivery: delivery method chosen for the order
    Payment: payment method chosen for the order
    Paid: True if the order was paid for, False otherwise
    """

    cart = models.OneToOneField(ShoppingCart, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Klient - zalogowany użytkownik",
    )
    guest_buyer_first_name = models.CharField(
        max_length=64, null=True, verbose_name="Klient - Gość - imię"
    )
    guest_buyer_last_name = models.CharField(
        max_length=64, null=True, verbose_name="Klient - Gość - nazwisko"
    )
    guest_buyer_email = models.EmailField(
        null=True, verbose_name="Klient - Gość - email"
    )
    address_city = models.CharField(max_length=64, verbose_name="Miasto")
    address_zipcode = models.CharField(
        max_length=6,
        validators=[RegexValidator(regex=r"\d{2}-\d{3}")],
        verbose_name="Kod pocztowy",
    )
    address_street = models.CharField(max_length=64, verbose_name="Ulica")
    address_country = models.CharField(max_length=64, verbose_name="Kraj")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Data zamówienia")
    delivery = models.CharField(
        max_length=32,
        choices=[("Kurier", "Kurier"), ("Odbiór własny", "Odbiór własny")],
        verbose_name="Sposób dostawy",
    )
    payment = models.CharField(
        max_length=32,
        choices=[
            ("Przelew", "Przelew"),
            ("Płatność przy odbiorze", "Płatność przy odbiorze"),
        ],
        verbose_name="Sposób płatności",
    )
    paid = models.BooleanField(default=False, verbose_name="Zapłacone")

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"

    def __str__(self):
        output = f"Zamówienie nr: {self.id}"
        return output


class CarService(models.Model):
    """
    Name: name of the car service
    Price: price of the car service
    Time: duration of the car service, in hours
    """

    name = models.CharField(max_length=64, verbose_name="Nazwa usługi")
    price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Cena", null=True
    )
    time = models.IntegerField(verbose_name="Czas trwania", null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Warsztat - usługa"
        verbose_name_plural = "Warsztat - usługi"
