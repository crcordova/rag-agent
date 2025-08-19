import os
from dotenv import load_dotenv

load_dotenv()
UPLOAD_DIR = "./uploads"
PERSIST_DIR = "./storage"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
USE_QDRANT = os.getenv("USE_QDRANT", "True") == "True"
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
DEVICE = os.getenv("DEVICE", "cpu")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
EMBEDDING_PROVIDER=os.getenv("EMBEDDING_PROVIDER", "huggingface")  
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "hkunlp/instructor-base")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")