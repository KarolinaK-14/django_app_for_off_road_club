# Generated by Django 3.1.5 on 2021-02-28 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('niunius', '0026_auto_20210228_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='code',
            field=models.CharField(max_length=128, unique=True, verbose_name='Kod produktu'),
        ),
    ]
