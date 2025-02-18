from spotipy.exceptions import SpotifyException
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError
import os
import time
import requests
import random
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from mood_analyzer import analyze_closest_genre_with_gemini

load_dotenv()

session = requests.Session()
session.request = lambda *args, **kwargs: requests.request(*args, timeout=10, **kwargs)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-modify-public",
    )
)

FALLBACK_GENRES = [
    "pop", "rock", "hip-hop", "jazz", "classical", "electronic", "metal", "country",
    "indie", "folk", "blues", "soul", "punk", "funk", "disco", "reggae", "gospel",
    "r&b", "trap", "lofi", "house", "techno", "samba", "sertanejo", "pagode",
    "forro", "axé", "mpb", "bossa nova", "emo", "emocore", "hardcore", "grunge",
    "ska", "drum and bass", "dubstep", "trance", "k-pop", "j-pop", "c-pop",
    "rap", "reggaeton", "dancehall", "mariachi", "tango", "flamenco", "blues rock",
    "alternative", "shoegaze", "post-rock", "new wave", "synthpop", "garage rock",
    "progressive rock", "hard rock", "heavy metal", "black metal", "death metal",
    "power metal", "nu metal", "metalcore", "math rock", "stoner rock", "post-punk",
    "art rock", "symphonic metal", "industrial", "opera", "ambient", "chillout",
    "minimal", "experimental", "downtempo", "psych rock", "neo soul", "boogie",
    "swing", "bebop", "latin", "afrobeat", "highlife", "cumbia", "bachata",
    "zouk", "soca", "balkan", "gypsy jazz", "drone", "hyperpop", "vaporwave",
    "phonk", "chiptune", "soundtrack", "video game music", "score", "epic",
    "medieval", "chant", "bluegrass", "americana", "cajun", "zydeco",
    "bolero", "tropical", "celtic", "world music", "indian classical",
    "hindustani", "kathak", "ghazal", "qawwali", "persian", "turkish",
    "greek", "arabic", "flamenco", "fado", "mandopop", "afrobeats", "drill",
    "grime", "jazz fusion", "smooth jazz", "lounge", "baroque", "chamber music",
    "musical", "christmas", "caribbean", "island", "hawaiian", "polka", "yodeling"
]

def get_user_id():
    """ Obtém o ID do usuário autenticado no Spotify """
    user_info = sp.current_user()
    return user_info["id"]



# 🔹 Função para obter um token de acesso à API do Spotify
def get_access_token():
    auth_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    }
    response = requests.post(auth_url, data=data)
    token_info = response.json()
    return token_info.get("access_token")


# 🔹 Função para obter todos os gêneros disponíveis no Spotify
def get_available_genres():
    token = get_access_token()
    if not token:
        print("[ERRO] Falha ao obter token de acesso. Usando fallback de gêneros.")
        return FALLBACK_GENRES

    url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[ERRO] Não foi possível obter a lista de gêneros. Código {response.status_code}. Usando fallback.")
        return FALLBACK_GENRES

    genres = response.json().get("genres", [])
    if not genres:
        print("[ERRO] A API do Spotify não retornou gêneros. Usando fallback.")
        return FALLBACK_GENRES

    return genres


def search_songs_by_criteria(mood, genre=None, artist=None, limit=10):
    """
    Busca músicas no Spotify baseadas nos critérios do usuário.

    Parâmetros:
    - mood: Humor do usuário.
    - genre: Gênero musical desejado.
    - artist: Artista(s) sugeridos.
    - limit: Número de músicas a buscar.

    Retorna:
    - Lista de URIs das músicas encontradas.
    """
    query_parts = []

    if genre:
        query_parts.append(f"genre:{genre}")  # 🔹 Sempre buscar por gênero
    if artist:
        query_parts.append(f"artist:{artist}")

    search_query = " ".join(query_parts)

    print(f"[DEBUG] Query para Spotify: {search_query}, buscando {limit} músicas populares")

    collected_tracks = []
    max_retries = 3  # Tentativas caso ocorra erro na API

    for attempt in range(max_retries):
        try:
            results = sp.search(q=search_query, type="track", limit=limit, offset=0)
            break  # Se a requisição deu certo, sai do loop
        except (ReadTimeout, ConnectionError, HTTPError) as e:
            print(f"[ERRO] Falha ({type(e).__name__}) na tentativa {attempt + 1}/{max_retries}. Retentando...")
            time.sleep(2)
        except SpotifyException as e:
            print(f"[ERRO] Erro do Spotify: {e}. Tentativa {attempt + 1}/{max_retries}")
            time.sleep(2)

    else:
        print("[ERRO] Falha ao buscar músicas após várias tentativas. Retornando vazio.")
        return []

    if "tracks" not in results or not results["tracks"]["items"]:
        print("[ERRO] Nenhuma música encontrada!")
        return []

    # 🔹 Ordena por popularidade e remove duplicatas
    tracks = results["tracks"]["items"]
    tracks = sorted(tracks, key=lambda x: x["popularity"], reverse=True)  # 🔥 Prioriza músicas populares
    track_uris = list(dict.fromkeys([track["uri"] for track in tracks]))  # 🔄 Remove duplicatas mantendo ordem

    # 🔹 Garante que estamos retornando no máximo `limit` músicas
    track_uris = track_uris[:limit]

    print(f"[DEBUG] Tracks filtradas ({len(track_uris)}): {track_uris}")
    return track_uris



# def get_recommended_tracks(mood, genres=None, artists=None, countries=None, limit=10):
#     """Busca recomendações balanceadas de músicas no Spotify com base no humor e preferências."""
#     genres = genres.split(",") if genres else []  # Transforma string separada por vírgulas em lista
#     artists = artists.split(",") if artists else []
#     countries = countries.split(",") if countries else []
#
#     total_sources = max(1, len(genres) + len(artists) + len(countries))  # Garante pelo menos 1 fonte
#     limit_per_source = max(1, limit // total_sources)  # Divide as buscas de forma equilibrada
#     remaining_tracks = limit % total_sources  # Distribui o resto das músicas
#
#     mood_attributes = {
#         "feliz": {"valence": 0.8, "energy": 0.7},
#         "triste": {"valence": 0.2, "energy": 0.3},
#         "relaxado": {"valence": 0.5, "energy": 0.2},
#         "animado": {"valence": 0.9, "energy": 0.8}
#     }
#
#     attributes = mood_attributes.get(mood, {"valence": 0.5, "energy": 0.5})
#
#     all_tracks = []
#
#     def fetch_recommendations(seed_genres, seed_artists, country, count):
#         """Busca recomendações no Spotify para os parâmetros informados."""
#         try:
#             recommendations = sp.recommendations(
#                 seed_genres=seed_genres[:1],  # Spotify aceita no máximo 1 gênero como semente
#                 seed_artists=seed_artists[:1],  # Spotify aceita no máximo 1 artista
#                 target_valence=attributes["valence"],
#                 target_energy=attributes["energy"],
#                 limit=count
#             )
#             return [track["uri"] for track in recommendations["tracks"]]
#         except Exception as e:
#             print(f"[ERRO] Falha ao buscar recomendações para {seed_genres}, {seed_artists}, {country}: {e}")
#             return []
#
#     # Alterna entre gêneros, artistas e países para balancear a busca
#     for i in range(max(len(genres), len(artists), len(countries))):
#         genre = genres[i % len(genres)] if genres else None
#         artist = artists[i % len(artists)] if artists else None
#         country = countries[i % len(countries)] if countries else None
#         track_count = limit_per_source + (1 if remaining_tracks > 0 else 0)
#         remaining_tracks -= 1
#
#         tracks = fetch_recommendations([genre] if genre else [], [artist] if artist else [], country, track_count)
#         all_tracks.extend(tracks)
#
#     # Embaralha as músicas para diversificação
#     random.shuffle(all_tracks)
#
#     print(f"[DEBUG] Tracks recomendadas ({len(all_tracks)}): {all_tracks[:limit]}")
#     return all_tracks[:limit]


def get_track_ids_from_names(track_names):
    track_ids = []
    for track_name in track_names:
        try:
            results = sp.search(q=track_name.replace("%", " "), type="track", limit=1)
            if results["tracks"]["items"]:
                track_uri = results["tracks"]["items"][0]["uri"]
                track_ids.append(track_uri)
            else:
                print(f"[ERRO] Nenhuma música encontrada para '{track_name}'")
        except Exception as e:
            print(f"[ERRO] Falha ao buscar ID da música '{track_name}': {e}")
        time.sleep(0.5)

    return track_ids



def create_playlist(mood, tracks, title):
    """
    Cria uma playlist no Spotify e adiciona as músicas encontradas.

    Parâmetros:
    - mood: O humor do usuário (usado no nome da playlist).
    - tracks: Lista de URIs das músicas.
    - title: Nome da playlist.

    Retorna:
    - Dicionário com nome e URL da playlist.
    """
    user_id = get_user_id()  # ⚠️ Certifique-se de que essa função está definida!

    if not tracks:
        print("[ERRO] Nenhuma música disponível para adicionar na playlist!")
        return {"error": "Nenhuma música disponível para adicionar na playlist."}

    playlist = sp.user_playlist_create(user=user_id, name=title, public=True)
    sp.playlist_add_items(playlist_id=playlist["id"], items=tracks)

    return {"name": title, "url": playlist["external_urls"]["spotify"]}

