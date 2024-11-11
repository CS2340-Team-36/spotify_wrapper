from django.db import models
from django.contrib.auth.models import User

class UserSpotifyData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_name = models.CharField(max_length=100)  # Name or label for each wrap
    top_tracks = models.JSONField()  # Use JSONField to store track data

    def __str__(self):
        return f"{self.wrap_name} for {self.user.username}"
