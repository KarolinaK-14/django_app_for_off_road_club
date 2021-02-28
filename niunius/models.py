from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Article(models.Model):
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
    updated = models.DateTimeField(auto_now=True, verbose_name="Zmieniono")
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
        return self.product_set.exclude(stock=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Car, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name="Nazwa")
    slug = models.SlugField(unique=True, blank=True, max_length=64)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"

    def __str__(self):
        return self.name

    def get_available_products(self):
        return self.product_set.exclude(stock=0)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name="Nazwa")
    slug = models.SlugField(unique=True, blank=True, max_length=128)
    added = models.DateTimeField(auto_now_add=True, verbose_name="Dodano")
    code = models.CharField(max_length=128, verbose_name="Kod produktu")
    stock = models.IntegerField(verbose_name="Dostępność")
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
    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Koszyk"
        verbose_name_plural = "Koszyki"

    def total(self):
        return sum([item.value for item in self.cartitem_set.all()])

    def __str__(self):
        return f"Koszyk nr: {self.id}"


class CartItem(models.Model):
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
    name: name of the car service
    price: price of the car service
    time: duration of the car service, in minutes
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
