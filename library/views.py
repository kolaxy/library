from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from .models import Author, Book, Genre
from .forms import BookCreate, AuthorCreate
from django.contrib import messages


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def book_create(request):
    if request.method == 'POST':
        form = BookCreate(request.POST)
        if form.is_valid():
            form.instance.creator = request.user
            form.save()
            messages.success(request, f'Страница для "{form.instance.name}" была создана.')
            return redirect('book-detail', pk=form.instance.pk)

    else:
        form = BookCreate()
    return render(request, 'book/book_create.html', {'form': form})


class BookDetailView(DetailView):
    model = Book
    template_name = 'book/book_detail.html'


def author_create(request):
    if request.method == 'POST':
        form = AuthorCreate(request.POST)
        if form.is_valid():
            form.instance.creator = request.user
            form.save()
            messages.success(request, f'Автор с именем "{form.instance.name}" был создан.')
            return redirect('author-detail', pk=form.instance.pk)

    else:
        form = AuthorCreate()
    return render(request, 'author/author_create.html', {'form': form})


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'author/author_detail.html'
