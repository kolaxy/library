from django.urls import path
from . import views
from .forms import BookCreate
from library.views import (
    BookDetailView,
)

urlpatterns = [
    path('', views.home, name='library-home'),
    path('about/', views.about, name='library-about'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/new/', views.book_create, name='book-create'),
    # path('authors/new/', AuthorCreateView.as_view(), name='author-create'),
]
