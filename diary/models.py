from django.db import models
from django.contrib.auth.models import User
from series.models import Series

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    season = models.PositiveIntegerField()
    watched_on = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-watched_on']   

    def __str__(self):
        return f"{self.user.username} watched {self.series.title} S{self.season} on {self.watched_on}"