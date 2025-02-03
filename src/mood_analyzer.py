import os
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

def get_mood(text):
    llm = OpenAI(api_key=api_key)
    response = llm(f"Qual é a emoção predominante neste texto? '{text}'")
    return response.lower().strip()
