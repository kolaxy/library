from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from .models import Author, Book, Genre
from .forms import BookCreate, AuthorCreate
from django.contrib import messages
from django.db.models import Q


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def search(request):
    if request.method == "GET":
        q = request.GET.get('q')
        books = Book.objects.filter(name__icontains=q)
        authors = Author.objects.filter(Q(family_name__icontains=q) |
                                        Q(name__icontains=q) |
                                        Q(surname__icontains=q))
        return render(request, 'search.html', {'q': q, 'books': books, 'authors': authors})
    else:
        return render(request, 'search.html', {})


class GenreAuthor:
    """Жанры и авторы книг"""

    def get_genres(self):
        return Genre.objects.all()

    def get_authors(self):
        return Author.objects.all()


class FilterBooksView(GenreAuthor, ListView):
    template_name = 'filter.html'
    context_object_name = 'books'

    def get_queryset(self):
        if 'genre' in self.request.GET and 'author' in self.request.GET:
            print('if genre and author')
            queryset = Book.objects.filter(
                Q(author__in=self.request.GET.getlist("author")), Q(genre__in=self.request.GET.getlist("genre"))
            )
        else:
            print('else')
            queryset = Book.objects.filter(
                Q(author__in=self.request.GET.getlist("author")) | Q(genre__in=self.request.GET.getlist("genre"))
            )
        return queryset


def book_create(request):
    if request.method == 'POST':
        form = BookCreate(request.POST, request.FILES)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fav = bool
        book = get_object_or_404(Book, id=self.kwargs['pk'])
        if book.favourites.filter(id=self.request.user.id).exists():
            fav = True
        context['fav'] = fav
        # self.request.user.id
        return context


class BookListView(GenreAuthor, ListView):
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


class AuthorDetailView(DetailView, MultipleObjectMixin):
    model = Author
    template_name = 'author/author_detail.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        object_list = Book.objects.filter(author=self.kwargs['pk'])
        context = super(AuthorDetailView, self).get_context_data(object_list=object_list, **kwargs)
        return context


class AuthorListView(ListView):
    model = Author
    context_object_name = 'authors'
    template_name = 'author/author_list.html'
    paginate_by = 10
