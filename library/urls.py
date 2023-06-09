from django.urls import path
from . import views
from library.views import (
    BookDetailView,
    BookListView,
    AuthorDetailView,
    AuthorListView,
    CommentEditView,
    TicketListView,
    TicketDetailView,

)

urlpatterns = [
    path('', views.home, name='library-home'),
    path('about/', views.about, name='library-about'),

    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genres/new', views.genre_create, name='genre-create'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genres/<int:id>/edit', views.genre_edit, name='genre-edit'),

    path('books/', BookListView.as_view(), name='books'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/new/', views.book_create, name='book-create'),
    path('books/<int:id>/edit/', views.book_edit, name='book-edit'),
    path('books/<int:id>/delete/', views.book_delete, name='book-delete'),
    path('books/<int:id>/restore', views.book_restore, name='book-restore'),

    path('authors/', AuthorListView.as_view(), name='authors'),
    path('authors/new/', views.author_create, name='author-create'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('authors/<int:id>/edit', views.author_edit, name='author-edit'),


    path('search/', views.search, name='search'),
    path('filter/', views.FilterBooksView.as_view(), name='filter'),

    path('comment/<int:id>/delete/', views.comment_delete, name='comment-delete'),
    path('comment/<int:pk>/edit/', views.CommentEditView.as_view(), name='comment-edit'),

    path('archive/comments/', views.CommentArchiveView.as_view(), name='comments-archive'),
    path('archive/comment/<int:id>/restore/', views.comment_restore, name='comment-restore'),
    path('archive/books/', views.BookArchiveView.as_view(), name='books-archive'),

    path('tickets/', TicketListView.as_view(), name='tickets'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket-details'),
    path('tickets/new/book/', views.ticket_book_create, name='ticket-create'),
    path('tickets/edit/book/<int:id>', views.ticket_book_edit, name='ticket-edit'),

]
