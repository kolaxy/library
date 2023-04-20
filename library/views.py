from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Author, Book, Genre
from .forms import BookCreate, AuthorCreate
from django.contrib import messages
from django.db.models import Q


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        books = Book.objects.filter(name__icontains=searched)
        authors = Author.objects.filter(Q(family_name__icontains=searched) |
                                        Q(name__icontains=searched) |
                                        Q(surname__icontains=searched))
        return render(request, 'search.html', {'searched': searched, 'books': books, 'authors': authors})
    else:
        return render(request, 'search.html', {})


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


class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/book_list.html'
    paginate_by = 10


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_list'] = Book.objects.filter(author=self.kwargs['pk'])
        return context


class AuthorListView(ListView):
    model = Author
    context_object_name = 'authors'
    template_name = 'author/author_list.html'
    paginate_by = 10
