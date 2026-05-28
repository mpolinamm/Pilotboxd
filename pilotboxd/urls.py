from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('series.urls')),
    path('accounts/', include('accounts.urls')),
    path('diary/', include('diary.urls')),
]