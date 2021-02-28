# Generated by Django 3.1.5 on 2021-02-27 21:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('niunius', '0022_auto_20210227_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='update', to=settings.AUTH_USER_MODEL, verbose_name='Zmienione przez'),
        ),
    ]