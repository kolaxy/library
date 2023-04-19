from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from .models import Author, Book, Genre
from .forms import BookCreate


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
            return redirect('library-home')

    else:
        form = BookCreate()
    return render(request, 'book/book_create.html', {'form': form})


# class BookCreateView(CreateView):
#     model = Book
#     fields = ['name', 'annotation', 'isbn', 'genre', 'author']
#     template_name = 'book/book_create.html'
#
#     def form_valid(self, form):
#         form.instance.creator = self.request.user
#         return super().form_valid(form)


class BookDetailView(DetailView):
    model = Book
    template_name = 'book/book_detail.html'


# class AuthorCreateView(CreateView):
#     model = Author
#     template_name = 'author/author_create.html'
