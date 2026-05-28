from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
from .models import Series, Review
from .forms import ReviewForm
from django.conf import settings
from tmdbv3api import TMDb, TV
import re

def series_list(request):
    series = Series.objects.all()
    alpha = [s for s in series if s.title and s.title[0].isalpha()]
    numeric = [s for s in series if s.title and not s.title[0].isalpha()]
    
    alpha.sort(key=lambda s: s.title.lower())
    numeric.sort(key=lambda s: s.title.lower())
    
    series = alpha + numeric
    return render(request, 'series/series_list.html', {'series': series})

def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    max_season = request.GET.get('max_season')

    if max_season:
        reviews = Review.objects.filter(
            series=series,
            season__lte=max_season   
        ).order_by('season', '-created_at')
    else:
        reviews = Review.objects.filter(series=series).order_by('season', '-created_at')

    season_range = range(1, series.total_seasons + 1)

    return render(request, 'series/series_detail.html', {
        'series': series,
        'reviews': reviews,
        'season_range': season_range,
        'max_season': int(max_season) if max_season else None,
    })

@login_required
def add_review(request, pk):
    series = get_object_or_404(Series, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.series = series
            review.save()
            return redirect('series_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'series/add_review.html', {'form': form, 'series': series})

def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        tmdb = TMDb()
        tmdb.api_key = settings.TMDB_API_KEY
        tv = TV()
        search_results = tv.search(query)
        results = search_results

    return render(request, 'series/search.html', {
        'results': results,
        'query': query,
    })

def add_from_tmdb(request, tmdb_id):
    tmdb = TMDb()
    tmdb.api_key = settings.TMDB_API_KEY
    tv = TV()
    show = tv.details(tmdb_id)

    series, created = Series.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            'title': show.name,
            'description': show.overview,
            'total_seasons': show.number_of_seasons,
            'poster_path': show.poster_path,
        }
    )

    return redirect('series_detail', pk=series.pk)