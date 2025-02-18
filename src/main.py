from fastapi import FastAPI, Query
from mood_analyzer import analyze_mood_and_preferences, analyze_mood_title
from spotify_client import (
    create_playlist,
    search_songs_by_criteria,
    get_track_ids_from_names,
)

app = FastAPI()


app = FastAPI()


@app.get("/recommend")
def recommend_music(
    text: str, limit: int = Query(10, description="Número de músicas a buscar")
):
    """
    Endpoint para recomendar músicas baseado no humor do usuário.

    Parâmetros:
    - text: Texto descrevendo o humor e preferências musicais.
    - limit: Quantidade de músicas a serem retornadas (padrão: 10).
    """
    mood_data = analyze_mood_and_preferences(text, limit)

    if not mood_data:
        return {"error": "Não foi possível processar a solicitação."}

    title = analyze_mood_title(text)
    mood = mood_data.get("mood")
    genres = mood_data.get("genre")
    artists = mood_data.get("artist")
    countries = mood_data.get("country")
    tracks = mood_data.get("tracks", [])

    print(f"[DEBUG] Músicas sugeridas pelo Gemini: {tracks}")

    if len(tracks) < limit:
        print(
            f"[INFO] Gemini retornou apenas {len(tracks)} músicas. Buscando mais {limit - len(tracks)} no Spotify..."
        )
        extra_tracks = search_songs_by_criteria(
            mood, genres, artists, countries, limit - len(tracks)
        )
        tracks.extend(extra_tracks)

    if not tracks:
        return {"error": "Nenhuma música encontrada para os critérios informados."}

    track_uris = get_track_ids_from_names(tracks)

    if not track_uris:
        return {"error": "Não foi possível encontrar IDs das músicas no Spotify."}

    playlist = create_playlist(mood, track_uris, title)

    return {
        "mood": mood,
        "playlist": playlist,
        "tracks_found": len(track_uris),
        "tracks": track_uris,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
