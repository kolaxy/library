from django.shortcuts import render
from django.views.generic.detail import DetailView
from .models import Author, Book, Genre


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


class BookDetailView(DetailView):
    model = Book
    template_name = 'book/book_detail.html'
