import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json
import random

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-pro", temperature=0.7, google_api_key=api_key
)


def analyze_mood_and_preferences(text, limit):
    artistas = max(2, int(limit / 5))
    musicas_minimas = max(5, limit)

    prompt = f"""Você é um assistente de IA especializado em entender emoções e preferências musicais.
    Dado o seguinte texto do usuário: "{text}", identifique as seguintes informações:

    - **Mood** (emoção predominante): Pode ser 'feliz', 'triste', 'relaxado', 'animado', etc.
    - **Genre** (gênero musical): Se o usuário mencionou um gênero, extraia-o (exemplo: rock, pop, jazz).
    - **Artist** (artista): Se o usuário mencionou um artista, extraia o nome do artista.
    - **Country** (país): Se o usuário mencionou um país, extraia o nome do país.

    ### 🎵 REGRAS PARA GERAÇÃO DE ARTISTAS E MÚSICAS:
    1. **Se for identificado um gênero musical**, **sugira pelo menos {artistas} artistas** populares desse gênero que estejam em alta, garantindo que sejam reconhecidos pelo Spotify.
    2. **Se o usuário não mencionou um gênero, identifique um baseado no humor predominante** e sugira artistas populares desse gênero.
    3. **Sempre gere pelo menos {musicas_minimas} músicas sugeridas** para a playlist, **priorizando músicas populares e recentes**.
    4. **Se nenhuma música específica for mencionada, selecione automaticamente músicas populares do gênero indicado**.

    ### 🔥 FORMATO DAS MÚSICAS:
    - **Substitua espaços por `%`** nos nomes das músicas e artistas (exemplo: `"Radioactive%Imagine%Dragons"`).
    - **Cada música deve conter o nome do artista junto** (exemplo: `"Bohemian%Rhapsody%Queen"`).
    - **Use formatação precisa para evitar erros na busca**.

    ### 📝 RESPOSTA JSON (SOMENTE O JSON, SEM EXPLICAÇÕES!):
    {{
        "mood": "feliz",
        "genre": "rock",
        "artist": "Coldplay, Imagine Dragons, Linkin Park, Foo Fighters, Red Hot Chili Peppers",
        "country": "EUA",
        "tracks": [
            "Radioactive%Imagine%Dragons",
            "Californication%Red%Hot%Chili%Peppers",
            "Best%of%You%Foo%Fighters"
        ]
    }}

    ### 🚀 OBSERVAÇÕES IMPORTANTES:
    - Se alguma informação não for mencionada, retorne `null` nesse campo.
    - **Se nenhuma música for identificada, selecione automaticamente músicas populares** do gênero identificado.
    - **Nunca retorne músicas com espaços!** Sempre use `%` no lugar de espaços.
    - Se o Gemini não conseguir sugerir músicas, **ele deve retornar `"tracks": []"` e o Spotify será usado**.

    **Gere apenas o JSON e nada mais.**
    """

    response = llm.invoke(prompt)
    if hasattr(response, "content"):
        json_content = response.content
    else:
        print("Erro: O objeto de resposta não tem um atributo 'content'.")
        return {"mood": "desconhecido", "genre": None, "artist": None, "country": None}

    try:
        result = json.loads(json_content)
        print(result)
        return result
    except json.JSONDecodeError:
        print("Erro ao interpretar JSON:", json_content)
        return {"mood": "desconhecido", "genre": None, "artist": None, "country": None}


def analyze_mood_title(text):
    prompt = f"""Você é um assistente de IA especializado em entender emoções e preferências musicais.
    Dado o seguinte texto do usuário: "{text}", identifique as seguintes informações:

    - **Mood** (emoção predominante): Pode ser 'feliz', 'triste', 'relaxado', 'animado', etc.
    - **Genre** (gênero musical): Se o usuário mencionou um gênero, extraia-o (exemplo: rock, pop, jazz).
    - **Artist** (artista): Se o usuário mencionou um artista, extraia o nome do artista.
    - **Country** (país): Se o usuário mencionou um país, extraia o nome do país.

    Com base nesses dados, gere um **título engraçado** para a playlist com no máximo **20 caracteres**.

    Exemplos:
    - "Estou feliz e quero um samba" → "Sambando na Felicidade"
    - "Quero rock triste" → "Headbanging e Choro"
    - "Pop animado dos EUA" → "Pop Star na Veia"

    **Saída esperada:** Apenas o título gerado, sem explicações adicionais.
    """

    response = llm.invoke(prompt)

    title = response.content.strip().split("\n")[0]

    title = title[:20].strip()

    print(f"[DEBUG] Título gerado: {title}")  # Log para depuração

    return title


def analyze_closest_genre_with_gemini(user_genre, available_genres):
    """
    Consulta o Gemini para encontrar um gênero equivalente ao informado pelo usuário.

    Parâmetros:
    - user_genre: O gênero informado pelo usuário.
    - available_genres: Lista de gêneros válidos do Spotify.

    Retorna:
    - O gênero mais próximo encontrado.
    """

    prompt = f"""
    O usuário mencionou um gênero musical: "{user_genre}". No entanto, este gênero não está disponível no Spotify.

    Aqui está uma lista de gêneros disponíveis no Spotify:
    {", ".join(available_genres)}

    Com base na sua experiência e conhecimento musical, qual gênero da lista acima é o mais próximo do gênero informado pelo usuário?

    **Responda apenas com um dos gêneros da lista, sem explicações adicionais.**
    """

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        suggested_genre = response.content.strip()
        if suggested_genre in available_genres:
            print(f"[INFO] Gemini sugeriu o gênero '{suggested_genre}' como alternativa.")
            return suggested_genre
        else:
            print("[ERRO] O Gemini retornou um gênero inválido. Usando uma alternativa aleatória.")
            return random.choice(available_genres)
    else:
        print("[ERRO] Falha ao obter resposta do Gemini. Selecionando gênero aleatório.")
        return random.choice(available_genres)