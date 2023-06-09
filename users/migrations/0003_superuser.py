# Generated by Django 4.2 on 2023-04-24 08:15

from django.db import migrations, models
from django.contrib.auth.models import User


def create_superuser(apps, schema_editor):
    user = User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin'
    )


def add_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.bulk_create([
        Group(name=u'Librarians'),
        Group(name=u'Readers'),
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_alter_profile_image'),
    ]

    operations = [
        migrations.RunPython(add_groups),
        migrations.RunPython(create_superuser),
    ]
