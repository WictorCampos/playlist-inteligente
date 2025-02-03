import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

mood_playlists = {
    "feliz": "spotify:playlist:37i9dQZF1DXdPec7aLTmlC",
    "triste": "spotify:playlist:37i9dQZF1DX3YSRoSdA634",
    "relaxado": "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY",
    "animado": "spotify:playlist:37i9dQZF1DX0bX3Tks5cAZ"
}

def get_playlist_by_mood(mood):
    playlist_uri = mood_playlists.get(mood, "spotify:playlist:37i9dQZF1DX3YSRoSdA634")  # Padrão: Triste
    playlist = sp.playlist(playlist_uri)
    return {"name": playlist["name"], "url": playlist["external_urls"]["spotify"]}
