import os
import shutil
from fastapi import HTTPException
import hashlib
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.storage.docstore import SimpleDocumentStore
from ..config import UPLOAD_DIR, PERSIST_DIR, COLLECTION_NAME
from ..vector_store import get_vector_store

def _get_file_hash(file_obj):
    """Genera un hash SHA256 para identificar el contenido del archivo"""
    hash_sha256 = hashlib.sha256()
    file_obj.seek(0)  # Asegurarse de empezar desde el inicio
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hash_sha256.update(chunk)
    file_obj.seek(0)  # Volver al inicio para poder guardarlo después
    return hash_sha256.hexdigest()

def process_pdf(file):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    file_hash = _get_file_hash(file.file)
    for existing_file in os.listdir(UPLOAD_DIR):
        existing_path = os.path.join(UPLOAD_DIR, existing_file)
        with open(existing_path, "rb") as f:
            if _get_file_hash(f) == file_hash:
                raise HTTPException(
                    status_code=400, 
                    detail=f"El documento '{file.filename}' ya fue subido anteriormente."
                )

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        documents = SimpleDirectoryReader(input_dir=UPLOAD_DIR).load_data()
        vector_store = get_vector_store()

        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            storage_context=storage_context
        )
        index.storage_context.persist(persist_dir=PERSIST_DIR)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el documento: {str(e)}")

def reset_index():
    try:
        # 1. Eliminar PDFs
        for file in os.listdir(UPLOAD_DIR):
            if file.lower().endswith(".pdf"):
                os.remove(os.path.join(UPLOAD_DIR, file))

        # 2. Eliminar colección en Qdrant
        vector_store = get_vector_store()
        client = vector_store.client  # QdrantClient
        client.delete_collection(collection_name=COLLECTION_NAME)

        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)  # borra toda la carpeta
            os.makedirs(PERSIST_DIR, exist_ok=True)  # recrear carpeta vacía

        return {"status": "success", "message": "Índice y PDFs eliminados correctamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reiniciar el índice: {str(e)}")