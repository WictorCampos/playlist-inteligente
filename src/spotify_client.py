import os
from dotenv import load_dotenv
import random
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError
import requests

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


def get_user_id():
    user_info = sp.current_user()
    return user_info["id"]


def search_songs_by_criteria(mood, genre=None, artist=None, country=None, limit=10):
    query_parts = []

    if genre:
        query_parts.append(f"genre:{genre}")  # 🔹 Sempre buscar por gênero
    if artist:
        query_parts.append(f"artist:{artist}")
    if country:
        query_parts.append(f"market:{country}")

    search_query = " ".join(query_parts)

    print(
        f"[DEBUG] Query para Spotify: {search_query}, buscando {limit} músicas populares"
    )

    collected_tracks = []
    max_retries = 3  # Tenta buscar até 3 vezes se der erro

    for attempt in range(max_retries):
        try:
            results = sp.search(q=search_query, type="track", limit=limit, offset=0)
            break  # Se a requisição deu certo, sai do loop
        except (ReadTimeout, ConnectionError, HTTPError) as e:
            print(
                f"[ERRO] Falha ({type(e).__name__}) na tentativa {attempt + 1}/{max_retries}. Retentando..."
            )
            time.sleep(2)
        except SpotifyException as e:
            print(f"[ERRO] Erro do Spotify: {e}. Tentativa {attempt + 1}/{max_retries}")
            time.sleep(2)

    else:
        print(
            "[ERRO] Falha ao buscar músicas após várias tentativas. Retornando vazio."
        )
        return []

    if "tracks" not in results or not results["tracks"]["items"]:
        print("[ERRO] Nenhuma música encontrada!")
        return []

    # 🔹 Ordena por popularidade e remove duplicatas
    tracks = results["tracks"]["items"]
    tracks = sorted(
        tracks, key=lambda x: x["popularity"], reverse=True
    )  # 🔥 Mantém só as mais populares
    track_uris = list(
        dict.fromkeys([track["uri"] for track in tracks])
    )  # 🔄 Remove duplicatas mantendo ordem

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
    """
    Obtém os IDs do Spotify para uma lista de nomes de músicas.

    Parâmetros:
    - track_names: Lista de nomes de músicas.

    Retorna:
    - Lista de URIs do Spotify para as músicas encontradas.
    """
    track_ids = []
    for track_name in track_names:
        try:
            results = sp.search(q=track_name, type="track", limit=1)
            if results["tracks"]["items"]:
                track_ids.append(results["tracks"]["items"][0]["uri"])
        except Exception as e:
            print(f"[ERRO] Falha ao buscar ID da música '{track_name}': {e}")
        time.sleep(0.5)

    return track_ids


def create_playlist(mood, tracks, title):
    user_id = get_user_id()
    if not tracks:
        print("[ERRO] Nenhuma música disponível para adicionar na playlist!")
        return {"error": "Nenhuma música disponível para adicionar na playlist."}

    playlist_name = title

    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    sp.playlist_add_items(playlist_id=playlist["id"], items=tracks)

    return {"name": playlist_name, "url": playlist["external_urls"]["spotify"]}
