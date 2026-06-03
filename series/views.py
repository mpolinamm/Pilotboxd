from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Series, Review
from diary.models import DiaryEntry
from .forms import ReviewForm
from django.conf import settings
from tmdbv3api import TMDb, TV
from django import forms
from django.db.models import Avg

def series_list(request):
    series = Series.objects.annotate(avg_rating=Avg('reviews__rating'))
    alpha = [s for s in series if s.title and s.title[0].isalpha()]
    numeric = [s for s in series if s.title and not s.title[0].isalpha()]
    alpha.sort(key=lambda s: s.title.lower())
    numeric.sort(key=lambda s: s.title.lower())
    series = alpha + numeric
    return render(request, 'series/series_list.html', {'series': series})

def series_detail(request, pk):
    series = get_object_or_404(Series, pk=pk)
    series.avg_rating = Review.objects.filter(series=series).aggregate(Avg('rating'))['rating__avg']
    max_season = request.GET.get('max_season')

    if max_season:
        reviews = Review.objects.filter(
            series=series,
            season__lte=max_season
        ).order_by('season', '-created_at')
    else:
        reviews = Review.objects.filter(series=series).order_by('season', '-created_at')

    season_range = range(1, series.total_seasons + 1)

    diary_entry = None
    if request.user.is_authenticated:
        diary_entry = DiaryEntry.objects.filter(user=request.user, series=series).first()

    return render(request, 'series/series_detail.html', {
        'series': series,
        'reviews': reviews,
        'season_range': season_range,
        'max_season': int(max_season) if max_season else None,
        'diary_entry': diary_entry,
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
    form.fields['season'].widget = forms.Select(
        choices=[(i, f'Season {i}') for i in range(1, series.total_seasons + 1)]
    )
    return render(request, 'series/add_review.html', {'form': form, 'series': series})

def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        tmdb = TMDb()
        tmdb.api_key = settings.TMDB_API_KEY
        tv = TV()
        search_results = tv.search(query)

        existing = {
            s.tmdb_id: s.pk
            for s in Series.objects.filter(tmdb_id__isnull=False)
        }

        for show in search_results:
            if not hasattr(show, 'id'):
                continue
            if show.id:
                series_pk = existing.get(show.id)
                results.append({
                    'id': show.id,
                    'name': show.name,
                    'overview': show.overview,
                    'first_air_date': show.first_air_date,
                    'poster_path': show.poster_path,
                    'in_db': show.id in existing,
                    'series_pk': series_pk,
                })

    return render(request, 'series/search.html', {
        'results': results,
        'query': query,
    })

def add_from_tmdb(request, tmdb_id):
    tmdb = TMDb()
    tmdb.api_key = settings.TMDB_API_KEY
    tv = TV()
    show = tv.details(tmdb_id)

    series, _ = Series.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            'title': show.name,
            'description': show.overview,
            'total_seasons': show.number_of_seasons,
            'poster_path': show.poster_path,
        }
    )

    return redirect('series_detail', pk=series.pk)

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return redirect('series_detail', pk=review.series.pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('series_detail', pk=review.series.pk)
    else:
        form = ReviewForm(instance=review)
    form.fields['season'].widget = forms.Select(
        choices=[(i, f'Season {i}') for i in range(1, review.series.total_seasons + 1)]
    )
    return render(request, 'series/edit_review.html', {'form': form, 'review': review})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return redirect('series_detail', pk=review.series.pk)
    series_pk = review.series.pk
    review.delete()
    return redirect('series_detail', pk=series_pk)