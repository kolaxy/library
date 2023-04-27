from django.urls import path
from . import views
from library.views import (
    BookDetailView,
    BookListView,
    AuthorDetailView,
    AuthorListView,
    CommentEditView
)

urlpatterns = [
    path('', views.home, name='library-home'),
    path('about/', views.about, name='library-about'),

    path('books/', BookListView.as_view(), name='books'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/new/', views.book_create, name='book-create'),
    path('books/<int:id>/edit/', views.book_update, name='book-update'),
    path('books/<int:id>/delete/', views.book_delete, name='book-delete'),

    path('authors/', AuthorListView.as_view(), name='authors'),
    path('authors/new/', views.author_create, name='author-create'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),

    path('search/', views.search, name='search'),
    path('filter/', views.FilterBooksView.as_view(), name='filter'),

    path('comment/<int:id>/delete/', views.comment_delete, name='comment-delete'),
    path('comment/<int:pk>/edit/', views.CommentEditView.as_view(), name='comment-edit'),

    path('archive/comments/', views.CommentArchiveView.as_view(), name='comments-archive'),
    path('archive/comment/<int:id>/restore/', views.comment_restore, name='comment-restore'),
    path('archive/books/', views.BookArchiveView.as_view(), name='books-archive')
]
