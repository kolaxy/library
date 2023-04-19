from django import forms
from .models import *


class BookCreate(forms.ModelForm):

    class Meta:
        model = Book
        fields = ['name', 'genre', 'author', 'isbn', 'annotation']

        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            "genre": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Введите жанр'}),
            "author": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Автор'}),
            "isbn": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ISBN'}),
            "annotation": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите аннотация'})
        }

