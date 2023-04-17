from django.urls import path
from . import views
from library.views import (
    BookDetailView,
)

urlpatterns = [
    path('', views.home, name='library-home'),
    path('about/', views.about, name='library-about'),
    path('books/<int:pk>', BookDetailView.as_view(), name='book-detail'),
]
