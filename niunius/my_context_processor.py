from .models import Car, Category, Product


def my_cp(request):
    ctx = {
        "cars": Car.objects.all(),
        "categories": Category.objects.all(),
        "products": Product.objects.all(),
    }
    return ctx
