from .models import Car, Category


def my_cp(request):
    ctx = {
        "cars": Car.objects.all(),
        "categories": Category.objects.all(),
    }
    return ctx
