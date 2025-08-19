from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from .config import GROQ_API_KEY, DEVICE, EMBEDDING_MODEL,LLM_PROVIDER,EMBEDDING_PROVIDER, OPENAI_API_KEY,LLM_MODEL

if LLM_PROVIDER == "groq":
    if not GROQ_API_KEY:
        raise ValueError("Falta GROQ_API_KEY en el .env")
    llm = Groq(model=LLM_MODEL, temperature=0, api_key=GROQ_API_KEY)

elif LLM_PROVIDER == "openai":
    if not OPENAI_API_KEY:
        raise ValueError("Falta OPENAI_API_KEY en el .env")
    llm = OpenAI(model=LLM_MODEL, temperature=0, api_key=OPENAI_API_KEY)

else:
    raise ValueError(f"Proveedor LLM no soportado: {LLM_PROVIDER}")

# Configurar modelo de embeddings
if EMBEDDING_PROVIDER == "huggingface":
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL, device=DEVICE)

elif EMBEDDING_PROVIDER == "openai":
    from llama_index.embeddings.openai import OpenAIEmbedding
    if not OPENAI_API_KEY:
        raise ValueError("Falta OPENAI_API_KEY en el .env")
    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)

else:
    raise ValueError(f"Proveedor de embeddings no soportado: {EMBEDDING_PROVIDER}")

# Configuración global de LlamaIndex
Settings.embed_model = embed_model
Settings.llm = llm
