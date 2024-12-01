from django.db import models
from django.contrib.auth.models import User

class UserSpotifyData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_name = models.CharField(max_length=255)
    top_tracks = models.JSONField()  # Stores list of simplified track dictionaries
    top_artists = models.JSONField(null=True, blank=True)  # Add this for storing artist data
    term = models.CharField(
        max_length=50,
        choices=[
            ('short_term', 'Short Term'),
            ('medium_term', 'Medium Term'),
            ('long_term', 'Long Term'),
        ]
    )
    top_genres = models.JSONField(null=True, blank=True)  # Ensure this can store a list of genres
    llm_description = models.TextField(null=True, blank=True)  # New field for LLM description


