import random
import lyricsgenius
from django.conf import settings
import re

def get_lyric_snippet(song_name, artist_name):
    """Fetch a random lyric snippet using the lyricsgenius library."""
    api_key = settings.GENIUS_API_KEY
    genius = lyricsgenius.Genius(api_key, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
    genius.verbose = False  # Disable verbose output

    try:
        # Fetch the song from Genius
        song = genius.search_song(song_name, artist_name)
        if not song or not song.lyrics:
            print(f"No lyrics found for {song_name} by {artist_name}")
            return None

        # Split the lyrics into lines
        lyrics_lines = song.lyrics.split("\n")

        # Filter out lines that are metadata (like [Chorus], [Verse 1], etc.)
        lyrics_lines = [
            line for line in lyrics_lines
            if line.strip() and not re.match(r'^\[.*\]$', line.strip())
        ]

        if not lyrics_lines:
            return None

        # Return a random lyric line
        return random.choice(lyrics_lines)
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
        return None
