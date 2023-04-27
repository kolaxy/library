from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import (
    DetailView,
    ListView,
    UpdateView,
)
from .models import Author, Book, Genre, Comment
from .forms import BookCreate, AuthorCreate, CommentForm
from django.contrib import messages
from django.db.models import Q
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from django.utils.timezone import now


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


def book_update(request, id):
    book = Book.objects.get(pk=id)
    form = BookCreate(request.POST or None, request.FILES or None, instance=book)
    if form.is_valid():
        form.instance.creator = request.user
        form.save()
        messages.success(request, f'Страница "{form.instance.name}" была обновлена.')
        return redirect('book-detail', pk=form.instance.pk)
    return render(request, 'book/book_create.html', {'book': book, 'form': form})


def book_delete(request, id):
    try:
        book = Book.objects.get(pk=id)
        book.is_archive = True
        book.deletion_date = now()
        book.save()
        return redirect(request.META['HTTP_REFERER'])
    except Comment.DoesNotExist:
        return HttpResponseNotFound("<h2>Comment not found</h2>")


def comment_restore(request, id):
    try:
        comment = Comment.objects.get(id=id)
        comment.is_archive = False
        comment.deletion_date = None
        comment.save()
        return redirect(request.META['HTTP_REFERER'])
    except Comment.DoesNotExist:
        return HttpResponseNotFound("<h2>Comment not found</h2>")


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
        page = self.request.GET.get('page')
        context['comments'] = Comment.objects.filter(book=self.kwargs['pk'], is_archive=False).order_by(
            '-creation_time')
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
    paginate_by = 9


def comment_delete(request, id):
    try:
        comment = Comment.objects.get(id=id)
        comment.is_archive = True
        print('???')
        comment.deletion_date = now()
        comment.save()
        return redirect(request.META['HTTP_REFERER'])
    except Comment.DoesNotExist:
        return HttpResponseNotFound("<h2>Comment not found</h2>")


def comment_restore(request, id):
    try:
        comment = Comment.objects.get(id=id)
        comment.is_archive = False
        comment.deletion_date = None
        comment.save()
        return redirect(request.META['HTTP_REFERER'])
    except Comment.DoesNotExist:
        return HttpResponseNotFound("<h2>Comment not found</h2>")


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['name', 'body', ]
    template_name = 'comment/comment_edit.html'

    def form_valid(self, form):
        messages.success(self.request, "Рецензия изменена")
        form.instance.creator = self.request.user
        return super().form_valid(form)


class CommentArchiveView(LoginRequiredMixin, ListView):
    model = Comment
    queryset = Comment.objects.filter(is_archive=True)
    context_object_name = 'comments'
    template_name = 'comment/comments_archive.html'
    paginate_by = 10


class BookArchiveView(LoginRequiredMixin, ListView):
    model = Book
    queryset = Book.objects.filter(is_archive=True)
    context_object_name = 'books'
    template_name = 'book/book_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archive'] = True
        return context
