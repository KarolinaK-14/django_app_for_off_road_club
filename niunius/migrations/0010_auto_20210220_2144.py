# Generated by Django 3.1.5 on 2021-02-20 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('niunius', '0009_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default='2020-01-01', verbose_name='Data zamówienia'),
            preserve_default=False,
        ),
    ]