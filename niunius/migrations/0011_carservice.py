# Generated by Django 3.1.5 on 2021-02-20 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('niunius', '0010_auto_20210220_2144'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('notes', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Warsztat',
                'verbose_name_plural': 'Warsztat',
            },
        ),
    ]
