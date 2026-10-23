import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

def embeddings():
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Set GOOGLE_API_KEY in your local .env file.")
    return GoogleGenerativeAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001"))
