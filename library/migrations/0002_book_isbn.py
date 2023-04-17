# Generated by Django 4.2 on 2023-04-17 09:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=13, null=True, unique=True, validators=[django.core.validators.RegexValidator('^\\d{1,10}$')]),
        ),
    ]