from fastapi import APIRouter, Query
from ..services.query_service import run_query, summarize_docs_alternative, summarize_from_existing_vectorstore, analyze_document_relations

router = APIRouter()

@router.get("/query")
async def query_documents(q: str = Query(...)):
    '''Consulta abierta personalizada por el usuario para analizar documentos en el índice.'''
    response = run_query(q)
    return {"query": q, "response": response}

@router.get("/summarize-docs")
async def summarize_documents():
    '''Resume todos los documentos en el índice.
    Lee la carpeta de documentos y hace un resumen de su contenido.
    Con los resúmenes generados, se analizan las relaciones entre documentos.'''
    response = summarize_docs_alternative()
    relation = analyze_document_relations(response)
    return {"summary": response, "relations": relation}

@router.get("/summarize-docs_byvector")
async def summarize_documents():
    '''Resume los documentos que encuentra en los vectores no garantiza encontrar todos.
    hace un resumen de su contenido y busca relaciones entre documentos.'''
    response = summarize_from_existing_vectorstore()
    relation = analyze_document_relations(response)
    return {"summary": response, "relations": relation}