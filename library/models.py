from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from PIL import Image, ImageDraw, ImageFont
from django.http import JsonResponse
import os
import uuid
from io import BytesIO


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=30)
    is_archive = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    surname = models.CharField('Фамилия', max_length=30)
    name = models.CharField('Имя', max_length=30)
    family_name = models.CharField('Отчество', max_length=30)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_archive = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.surname} {self.name} {self.family_name}'


class Book(models.Model):
    @staticmethod
    def get_image_id():
        try:
            queryset = Book.objects.all().order_by('pk')
            last = queryset.last()
            last_id = last.id
            file_number = last_id + 1
        except:
            file_number = 1
        return str(file_number)

    def upload_to(self, filename):
        try:
            return f'book_pics/{self.pk}/{filename}'
        except:
            return f'book_pics/{self.get_image_id()}/{filename}'

    name = models.CharField('Название книги', max_length=30)
    annotation = models.TextField('Аннотация', max_length=1100)
    isbn = models.CharField('ISBN', max_length=13, validators=[RegexValidator(r'^\d{1,10}$')], unique=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    creation_time = models.DateTimeField(auto_now_add=True)

    is_archive = models.BooleanField(default=False)
    # mode = models.CharField(default='show')
    # ticket_key = models.IntegerField(default=None)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(User, related_name='favourite', default=None, blank=True)
    image = models.ImageField(default='book_pics/default.jpg', upload_to=upload_to, null=True, blank=True)
    deletion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    # def save(
    #         self, *args, **kwargs
    # ):
    #     super().save()
    #
    #     def convert_to_jpeg(im):
    #         with BytesIO() as f:
    #             im.save(f, format='JPEG')
    #             return f.getvalue()
    #
    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img = img.convert('RGB')
    #         img.save(self.image.path)


class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField(max_length=1100)
    creation_time = models.DateTimeField(auto_now_add=True)
    is_archive = models.BooleanField(default=False)
    deletion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.name}, {self.name}"

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.book.pk})


class Ticket(models.Model):
    playload = models.JSONField(default=dict)
    parent_key = models.IntegerField(blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_archive = models.BooleanField(default=False)
