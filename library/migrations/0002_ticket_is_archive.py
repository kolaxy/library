# Generated by Django 4.2 on 2023-05-01 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='is_archive',
            field=models.BooleanField(default=False),
        ),
    ]