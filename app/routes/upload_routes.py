from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from typing import List
from ..vector_store import get_qdrant_collection
from ..services.pdf_service import process_pdf, reset_index
from .. config import UPLOAD_DIR, PERSIST_DIR, USE_QDRANT, COLLECTION_NAME

router = APIRouter()

@router.post("/upload-pdf/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    '''Carga y vectoriza varios documentos PDF.'''
    resultados = []
    for file in files:
        try:
            process_pdf(file)
            resultados.append(f"Documento '{file.filename}' cargado y vectorizado")
        except Exception as e:
            resultados.append({"filename": file.filename, "status": "error", "detail": str(e)})
    
    return JSONResponse(content={"results": resultados})

@router.get("/list-documents/")
async def list_documents():
    """
    Devuelve la lista de archivos PDF cargados y estado del índice vectorial.
    """
    try:
        # 1. Archivos PDF subidos
        uploaded_files = [
            f for f in os.listdir(UPLOAD_DIR)
            if f.endswith(".pdf")
        ]

        # 2. Estado del índice vectorial
        if USE_QDRANT:

            collection_info = get_qdrant_collection()
            num_vectors = collection_info.vectors_count
            index_info = {
                "backend": "qdrant",
                "collection_name": COLLECTION_NAME,
                "num_vectors": num_vectors
            }
        else:
            # Modo local: contar cuántos archivos están persistidos
            persisted = os.listdir(PERSIST_DIR) if os.path.exists(PERSIST_DIR) else []
            index_info = {
                "backend": "local",
                "persisted_files": persisted,
                "num_items": len(persisted)
            }

        return {
            "uploaded_files": uploaded_files,
            "index_info": index_info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar documentos: {str(e)}")

@router.delete("/reset-index")
def reset_index_endpoint():
    '''Reinicia el índice vectorial. 
    Elimina los archivos .json, los archivos .pdf y los documentos en qdrant'''
    return reset_index()