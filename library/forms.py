from django import forms
from .models import *
from django.core.exceptions import ValidationError


class BookCreate(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'genre', 'author', 'isbn', 'annotation']

        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            "genre": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Введите жанр'}),
            "author": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Автор'}),
            "isbn": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ISBN'}),
            "annotation": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите аннотацию'})
        }


class AuthorCreate(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['surname', 'name', 'family_name']

        widgets = {
            "surname": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}),
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            "family_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите отчество'}),
        }

    def clean(self):
        data = self.cleaned_data
        if data == 'А Б В':
            raise ValidationError('Автор с таким именем уже существует!')
        return data


class FilterForm(forms.Form):
    publishers = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)
    authors = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), required=False)
