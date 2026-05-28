from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_seasons = models.PositiveIntegerField(default=1)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tmdb_id = models.IntegerField(unique=True, null=True, blank=True)
    poster_path = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Series"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='reviews')
    season = models.PositiveIntegerField()          
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'series', 'season')  
    def __str__(self):
        return f"{self.user.username} — {self.series.title} S{self.season} ({self.rating}★)"