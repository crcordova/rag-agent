from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes import upload_routes, query_routes
from app.models_config import embed_model, llm  # Inicializa configuración global


app = FastAPI(title="RAG Agent for PDF Analysis", description="API RAG Copilot", version="1.0.0")

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # permite frontend
    allow_credentials=True,
    allow_methods=["*"],     # permite todos los métodos, incluido OPTIONS
    allow_headers=["*"],
)

app.include_router(upload_routes.router)
app.include_router(query_routes.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)