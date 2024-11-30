import random
import lyricsgenius
from django.conf import settings

def get_lyric_snippet(song_name, artist_name):
    """Fetch a random lyric snippet using the lyricsgenius library."""
    api_key = settings.GENIUS_API_KEY
    genius = lyricsgenius.Genius(api_key)  # Initialize the Genius client

    try:
        # Fetch the song from Genius
        song = genius.search_song(song_name, artist_name)
        if not song or not song.lyrics:
            print(f"No lyrics found for {song_name} by {artist_name}")
            return None

        # Split the lyrics into lines and return a random non-empty line
        lyrics_lines = song.lyrics.split("\n")
        return random.choice([line for line in lyrics_lines if line.strip()])
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
        return None