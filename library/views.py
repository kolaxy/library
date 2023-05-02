import json
from random import randrange

from django.contrib.auth.models import User
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
from .models import Author, Book, Genre, Comment, Ticket
from .forms import BookCreate, AuthorCreate, CommentForm
from django.contrib import messages
from django.db.models import Q
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.http import JsonResponse
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
import shutil
from pathlib import Path


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
            queryset = Book.objects.filter(
                Q(author__in=self.request.GET.getlist("author")), Q(genre__in=self.request.GET.getlist("genre"))
            )
        else:
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


def book_edit(request, id):
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
        return redirect('books')
    except Book.DoesNotExist:
        return HttpResponseNotFound("<h2>Book not found</h2>")


def book_restore(request, id):
    try:
        book = Book.objects.get(id=id)
        book.is_archive = False
        book.deletion_date = None
        book.save()
        messages.success(request, f'Книга {book} была восстановлена')
        return redirect('books-archive')
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


class TicketListView(ListView):
    model = Ticket
    context_object_name = 'tickets'
    template_name = 'ticket/tickets_list.html'
    paginate_by = 10

    def get_queryset(self):
        return [(ticket.pk, json.loads(ticket.playload)) for ticket in
                Ticket.objects.filter(is_archive=False).order_by('-pk')]


class TicketDetailView(DetailView):
    model = Ticket
    context_object_name = 'ticket'
    template_name = 'ticket/ticket.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        ticket = Ticket.objects.get(pk=pk)
        ticket = (ticket.pk, json.loads(ticket.playload))
        return ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = Author.objects.get(pk=kwargs['object'][1]['author'])
        context['genre'] = Genre.objects.get(pk=kwargs['object'][1]['genre'])
        if kwargs['object'][1]['mode'] == 'book_edit':
            context['parent_model'] = Book.objects.get(pk=kwargs['object'][1]['id'])
            print(context['parent_model'].image)
        return context

    def post(self, request, *args, **kwargs):
        statusAccept = self.request.POST.get("action") == "accept"
        statusReject = self.request.POST.get("action") == "reject"
        if statusAccept:

            def isbn_valid(isbn):
                isbn_list = [bk.isbn for bk in Book.objects.all()]
                status = False
                while isbn in isbn_list:
                    status = True
                    isbn = str(randrange(1, 9999999999999))
                return isbn, status

            pk = self.kwargs.get('pk')
            ticket = Ticket.objects.get(pk=pk)
            ticket = json.loads(ticket.playload)
            img = ticket['image'].split('/')[1:]
            img_to_model = 'book_pics/default.jpg'
            if img[-1] == 'image.jpg':
                new_img_dir = os.path.join(settings.MEDIA_ROOT, f'book_pics/{Book.get_image_id()}/')
                src_dir = os.path.join(settings.MEDIA_ROOT, f'tickets/books/{pk}')
                dest_dir = new_img_dir
                files = os.listdir(src_dir)
                shutil.copytree(src_dir, dest_dir)
                img_to_model = f'book_pics/{Book.get_image_id()}/image.jpg'
            isbn_checked = isbn_valid(ticket['isbn'])
            book = Book(
                name=ticket['name'],
                genre=Genre.objects.get(pk=ticket['genre']),
                author=Author.objects.get(pk=ticket['author']),
                isbn=isbn_checked[0],
                annotation=ticket['annotation'],
                image=img_to_model,
                creator=User.objects.get(pk=ticket['creator']),
            )
            book.save()
            update = Ticket.objects.get(pk=pk)
            update.is_archive = True
            update.save()
            if isbn_checked[1]:
                messages.warning(request,
                                 f'''Заявка на создание "{book.name}" была одобрена.
                                  ISBN БЫЛ ЗАМЕНЕН НА СЛУЧАЙНЫЙ
                                   ИЗ-ЗА СОВПАДЕНИЯ С СУЩЕСТВУЮЩЕЙ МОДЕЛЬЮ!''')
            messages.success(request, f'Заявка на создание "{book.name}" была одобрена.')
            return redirect('book-detail', pk=book.pk)
        else:
            pk = self.kwargs.get('pk')
            ticket = Ticket.objects.get(pk=pk)
            book_name = json.loads(ticket.playload)['name']
            ticket.is_archive = True
            ticket.save()
            messages.warning(request, f'Заявка на создание "{book_name}" была отклонена.')
            return redirect('tickets')


def ticket_book_create(request):
    def get_id():
        try:
            queryset = Ticket.objects.all().order_by('pk')
            last = queryset.last()
            id_number = last.id + 1
        except:
            id_number = 1
        return str(id_number)

    if request.method == 'POST':
        form = BookCreate(request.POST, request.FILES)
        if form.is_valid():
            form.instance.creator = request.user
            form.cleaned_data['genre'] = form.cleaned_data['genre'].pk
            form.cleaned_data['author'] = form.cleaned_data['author'].pk
            form.cleaned_data['mode'] = 'book_add'
            form.cleaned_data['creator'] = request.user.id
            form.cleaned_data['creation_time'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            if request.FILES:
                data = request.FILES['image']
                form.cleaned_data.pop('image')
                path = default_storage.save(f'tickets/books/{get_id()}/image.jpg',
                                            ContentFile(data.read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                form.cleaned_data['image'] = f"media/tickets/books/{get_id()}/image.jpg"
            else:
                form.cleaned_data['image'] = f"media/book_pics/default.jpg"
            ticket_push = Ticket(playload=json.dumps(form.cleaned_data, ensure_ascii=False))
            ticket_push.creator = request.user
            ticket_push.save()

            messages.success(request, f'Заявка для "{form.instance.name}" была создана.')
            return redirect('library-home')
    else:
        form = BookCreate()
    return render(request, 'book/book_create.html', {'form': form})


def ticket_book_edit(request, id):
    def get_id():
        try:
            queryset = Ticket.objects.all().order_by('pk')
            last = queryset.last()
            id_number = last.id + 1
        except:
            id_number = 1
        return str(id_number)

    book = Book.objects.get(pk=id)
    form = BookCreate(request.POST or None, request.FILES or None, instance=book)

    if form.is_valid():
        form.instance.creator = request.user
        form.cleaned_data['id'] = id
        form.cleaned_data['genre'] = form.cleaned_data['genre'].pk
        form.cleaned_data['author'] = form.cleaned_data['author'].pk
        form.cleaned_data['mode'] = 'book_edit'
        form.cleaned_data['creator'] = request.user.id
        form.cleaned_data['creation_time'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if request.FILES:
            data = request.FILES['image']
            form.cleaned_data.pop('image')
            path = default_storage.save(f'tickets/books/{get_id()}/image.jpg',
                                        ContentFile(data.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            form.cleaned_data['image'] = f"media/tickets/books/{get_id()}/image.jpg"
        else:
            if os.path.isdir(f'media/book_pics/{id}'):
                form.cleaned_data['image'] = f'media/{str(Book.objects.get(pk=id).image)}'
                print(f'media/{str(Book.objects.get(pk=id).image)}')
            else:
                form.cleaned_data['image'] = f"media/book_pics/default.jpg"
        ticket_push = Ticket(playload=json.dumps(form.cleaned_data, ensure_ascii=False))
        ticket_push.creator = request.user
        ticket_push.save()
        messages.success(request, f'Заявка на обновление "{form.instance.name}" была создана.')
        return redirect('book-detail', pk=form.instance.pk)
    return render(request, 'book/book_create.html', {'book': book, 'form': form})
