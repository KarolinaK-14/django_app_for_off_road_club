# Generated by Django 3.1.5 on 2021-02-27 14:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('niunius', '0019_auto_20210227_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address_zipcode',
            field=models.CharField(max_length=6, validators=[django.core.validators.RegexValidator(regex='\\d{2}-\\d{3}')], verbose_name='Kod pocztowy'),
        ),
    ]
