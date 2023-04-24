from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView, MultipleObjectMixin
from .models import Author, Book, Genre, Comment
from .forms import BookCreate, AuthorCreate, CommentForm
from django.contrib import messages
from django.db.models import Q
from django.views.generic.edit import FormMixin


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


class BookDetailView(FormMixin, DetailView):
    model = Book
    template_name = 'book/book_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('book-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fav = bool
        book = get_object_or_404(Book, id=self.kwargs['pk'])
        if book.favourites.filter(id=self.request.user.id).exists():
            fav = True
        context['fav'] = fav
        context['comments'] = Comment.objects.filter(book=self.kwargs['pk'])
        context['form'] = CommentForm(initial={'book': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            form.instance.creator = request.user
            form.instance.book = Book.objects.get(id=self.kwargs['pk'])
            messages.success(request, f'Ваш комментарий создан.')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super(BookDetailView, self).form_valid(form)


class BookListView(GenreAuthor, ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'book/book_list.html'
    paginate_by = 9


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
