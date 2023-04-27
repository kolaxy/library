from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from PIL import Image, ImageDraw, ImageFont
import os
import uuid


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=30)

    def __str__(self):
        return self.name


class Author(models.Model):
    surname = models.CharField('Фамилия', max_length=30)
    name = models.CharField('Имя', max_length=30)
    family_name = models.CharField('Отчество', max_length=30)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_archive = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.surname} {self.name} {self.family_name}'


class Book(models.Model):
    @staticmethod
    def get_image_id():
        queryset = Book.objects.all().order_by('pk')
        last = queryset.last()
        last_id = last.id
        file_number = last_id + 1
        return str(file_number)

    def upload_to(self, filename):
        return f'book_pics/{self.get_image_id()}/{filename}'

    name = models.CharField('Название книги', max_length=30)
    annotation = models.TextField('Аннотация', max_length=1100)
    isbn = models.CharField('ISBN', max_length=13, validators=[RegexValidator(r'^\d{1,10}$')], unique=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    creation_time = models.DateTimeField(auto_now_add=True)
    is_archive = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(User, related_name='favourite', default=None, blank=True)
    image = models.ImageField(default='book_pics/default.jpg', upload_to=upload_to, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    def save(
            self, *args, **kwargs
    ):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField(max_length=1100)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.name}, {self.name}"

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.book.pk})
