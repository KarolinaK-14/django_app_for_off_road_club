# Generated by Django 3.1.5 on 2021-02-27 20:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('niunius', '0021_auto_20210227_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='slug',
            field=models.SlugField(blank=True, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='buyer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Klient - zalogowany użytkownik'),
        ),
        migrations.AlterField(
            model_name='order',
            name='guest_buyer_email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Klient - Gość - email'),
        ),
        migrations.AlterField(
            model_name='order',
            name='guest_buyer_first_name',
            field=models.CharField(max_length=64, null=True, verbose_name='Klient - Gość - imię'),
        ),
        migrations.AlterField(
            model_name='order',
            name='guest_buyer_last_name',
            field=models.CharField(max_length=64, null=True, verbose_name='Klient - Gość - nazwisko'),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=128, unique=True),
        ),
    ]