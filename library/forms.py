from django import forms
from django.db.models import Q

from .models import *
from django.core.exceptions import ValidationError


class BookCreate(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(BookCreate, self).__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.filter(
            Q(is_archive=False, is_accepted=True) | Q(creator=user, is_archive=False, is_accepted=False) | Q(creator=1))

    class Meta:
        model = Book
        fields = ['name', 'genre', 'author', 'isbn', 'annotation', 'image', ]

        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            "genre": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Введите жанр'}),
            "author": forms.Select(attrs={'class': 'form-control', 'placeholder': 'Автор'}),
            "isbn": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ISBN'}),
            "annotation": forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите аннотацию'}),
        }


class GenreCreate(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', ]


class AuthorCreate(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['surname', 'name', 'family_name', ]

        widgets = {
            "surname": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}),
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            "family_name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите отчество'}),
        }


class FilterForm(forms.Form):
    publishers = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)
    authors = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'body', ]

        widgets = {
            "name": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое резюме'}),
            "body": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Текст рецензии'}),
        }

#
# class TicketCreate(forms.ModelForm):
#     class Meta:
#         model = Ticket
#         fields =
