from fastapi import FastAPI
from mood_analyzer import get_mood
from spotify_client import get_playlist_by_mood

app = FastAPI()

@app.get("/recommend")
def recommend_music(text: str):
    mood = get_mood(text)
    playlist = get_playlist_by_mood(mood)
    return {"mood": mood, "playlist": playlist}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
