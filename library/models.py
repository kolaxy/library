from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Genre(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Author(models.Model):
    surname = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    family_name = models.CharField(max_length=30)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_archive = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.surname} {self.name} {self.family_name}'


class Book(models.Model):
    name = models.CharField(max_length=30)
    annotation = models.TextField()
    isbn = models.CharField(max_length=13, validators=[RegexValidator(r'^\d{1,10}$')], unique=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_archive = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})
