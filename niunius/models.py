from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)


class ArticlePhoto(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="niunius/blog_img")

    def __str__(self):
        return self.photo.name


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"komentarz dodany {self.added} przez {self.user}"


class Car(models.Model):
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="niunius/car_img/")

    @property
    def name(self):
        return f"{self.brand} {self.model}"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Car, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=128)
    stock = models.IntegerField()
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to="niunius/product_img/")
    cars = models.ManyToManyField(Car)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)


class Order(models.Model):
    def order_total(self):
        return sum([item.value for item in self.orderitem_set.all()])


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    @property
    def value(self):
        return self.quantity * self.product.price
