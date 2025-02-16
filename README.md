# Playlist Inteligente 🎵

Este projeto foi criado para recomendar músicas e montar playlists automaticamente com base no humor e preferências musicais do usuário. Ele utiliza **FastAPI**, **Gemini AI (Google)** e **Spotify API** para analisar sentimentos, buscar músicas e criar playlists personalizadas.

## 🚀 Como Funciona?

1. O usuário envia um texto descrevendo seu estado emocional e preferências musicais.
2. A IA (Google Gemini) interpreta o humor e sugere gêneros, artistas e possíveis músicas.
3. Se a IA não fornecer todas as músicas necessárias, o sistema busca músicas complementares no Spotify.
4. O sistema recupera os IDs das músicas e cria uma playlist personalizada no Spotify.
5. A playlist é criada e pode ser acessada via link!

---

## 📂 Estrutura do Projeto

```bash
📦 playlist-inteligente
├── 📂 src
│   ├── 📄 main.py                # API principal com FastAPI
│   ├── 📄 mood_analyzer.py       # Módulo que analisa o humor com Gemini AI
│   ├── 📄 spotify_client.py      # Cliente para integração com a API do Spotify
│   ├── 📄 .env                   # Variáveis de ambiente (API Keys)
├── 📄 .gitignore                 # Arquivos ignorados pelo Git
├── 📄 requirements.txt           # Dependências do projeto
└── 📄 README.md                  # Documentação do projeto
```

---

## 🛠 Tecnologias Utilizadas

- **FastAPI** → Para expor a API REST.
- **LangChain + Gemini AI** → Para interpretar emoções e sugerir músicas.
- **Spotify API** → Para buscar músicas e criar playlists.
- **Spotipy** → Cliente Python para interagir com o Spotify.
- **Requests/Dotenv** → Para requisições HTTP e gerenciamento de variáveis de ambiente.

---

## ⚙️ Configuração e Instalação

### 1️⃣ Clone o repositório:
```bash
git clone https://github.com/WictorCampos/playlist-inteligente.git
cd playlist-inteligente
```

### 2️⃣ Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

### 3️⃣ Instale as dependências:
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as credenciais no arquivo **.env** dentro da pasta `src/`:
```ini
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback
GEMINI_API_KEY=sua_api_key_do_gemini
```

---

## 🚀 Rodando a API

### Iniciar o servidor FastAPI:
```bash
cd src
uvicorn main:app --reload
```

A API estará disponível em:
```
http://127.0.0.1:8000/docs
```

---

## 📌 Endpoints Disponíveis

### 1️⃣ **Recomendar músicas**
```http
GET /recommend?text=<descrição_do_humor>&limit=<quantidade>
```

#### 📥 Exemplo de Requisição:
```http
GET /recommend?text=Quero um rock triste&limit=10
```

#### 📤 Exemplo de Resposta:
```json
{
  "mood": "triste",
  "playlist": {
    "name": "Rock no Sofrimento",
    "url": "https://open.spotify.com/playlist/xxxxx"
  },
  "tracks_found": 10,
  "tracks": [
    "spotify:track:XXXXXX",
    "spotify:track:YYYYYY"
  ]
}
```

---

## 📜 Como Funciona Cada Arquivo?

### 🏆 `main.py` → API Principal
- Expõe o endpoint `/recommend`.
- Chama a IA para entender o humor.
- Busca músicas com base nos dados retornados.
- Cria a playlist no Spotify e retorna o link.

### 🎭 `mood_analyzer.py` → Interpretação do Humor com Gemini AI
- Usa **LangChain + Gemini AI** para identificar emoções.
- Sugere gêneros, artistas e músicas baseados no humor.
- Se o Gemini não fornecer todas as músicas, o Spotify complementa.

### 🎧 `spotify_client.py` → Integração com o Spotify
- Se comunica com a **Spotify API** para:
  - Buscar músicas populares por gênero e artista.
  - Converter nomes de músicas em IDs do Spotify.
  - Criar playlists e adicionar as músicas selecionadas.

---

## 🏆 Diferenciais do Projeto

✅ **Gera playlists personalizadas com base no humor**
✅ **Usa IA (Gemini) para entender preferências**
✅ **Balanceia músicas entre diferentes gêneros e artistas**
✅ **Busca músicas populares e recentes automaticamente**
✅ **Cria playlists no Spotify com apenas um clique**

---

## 📌 Próximos Passos

🔹 Melhorar a precisão das sugestões musicais.
🔹 Adicionar suporte a outros serviços de música além do Spotify.
🔹 Criar uma interface web para interação mais amigável.

---

## 📞 Contato
Desenvolvido por **Wictor Rafael Gonçalves Campos**

🔗 GitHub: https://github.com/WictorCampos

Se tiver dúvidas ou sugestões, sinta-se à vontade para entrar em contato! 🎶🚀

