from django.urls import path
from . import views

urlpatterns = [
    path('', views.diary, name='diary'),
    path('add/<int:series_pk>/', views.add_entry, name='add_entry'),
]