from django.urls import path
from . import views

urlpatterns = [
    path('', views.series_list, name='series_list'),
    path('<int:pk>/', views.series_detail, name='series_detail'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('search/', views.search, name='search'),
    path('add/<int:tmdb_id>/', views.add_from_tmdb, name='add_from_tmdb'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
]