from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DiaryEntry
from series.models import Series
import datetime

@login_required
def diary(request):
    entries = DiaryEntry.objects.filter(user=request.user)
    return render(request, 'diary/diary.html', {'entries': entries})

@login_required
def add_entry(request, series_pk):
    series = get_object_or_404(Series, pk=series_pk)
    if request.method == 'POST':
        season = request.POST.get('season')
        notes = request.POST.get('notes', '')
        DiaryEntry.objects.create(
            user=request.user,
            series=series,
            season=season,
            watched_on=datetime.date.today(),
            notes=notes,
        )
        return redirect('series_detail', pk=series_pk)
    season_range = range(1, series.total_seasons + 1)
    return render(request, 'diary/add_entry.html', {
        'series': series,
        'season_range': season_range,
    })