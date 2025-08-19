from fastapi import HTTPException
from llama_index.core import StorageContext, VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever
from collections import defaultdict
import logging
from datetime import datetime

from ..config import PERSIST_DIR, COLLECTION_NAME, UPLOAD_DIR
from ..vector_store import get_vector_store
from ..prompts import SUMMARIZE_PROMPT, RELATION_PROMPT


SIMILARITY_THRESHOLD = 0.80
def run_query(question: str):
    try:
        vector_store = get_vector_store()
        client = vector_store.client
        info = client.get_collection(collection_name=COLLECTION_NAME)

        if info.vectors_count == 0:
            raise HTTPException(status_code=404, detail="No hay documentos indexados.")
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)

        query_engine = index.as_query_engine(
            similarity_top_k=10,
            node_postprocessing=[SimilarityPostprocessor(similarity_cutoff=SIMILARITY_THRESHOLD)]
        )

        response = query_engine.query(question)

        sources = []
        for n in (response.source_nodes or []):
            score = getattr(n, "score", None)
            if score is not None and score >= SIMILARITY_THRESHOLD:
                sources.append({
                    "score": score,
                    "doc_id": getattr(n.node, "ref_doc_id", None),
                    "snippet": (n.node.get_text() or "")[:200]
                })

        if not sources:
            return {
                "answer": "No encontré información relevante sobre esa pregunta en los documentos cargados.",
                "sources": []
            }

        return {
            "answer": str(response),
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {str(e)}")

def summarize_docs():
    try:
        vector_store = get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir=PERSIST_DIR)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
        
        # docs = index.storage_context.docstore.docs.values()
        docs = list(index.docstore.docs.values())
        if not docs:
            # Método 2: Usar retriever para obtener todos los documentos
            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=100  # Número alto para obtener todos los docs
            )
            retrieved_nodes = retriever.retrieve("documento contenido texto")
            if not retrieved_nodes:
                raise HTTPException(
                    status_code=404, 
                    detail="No hay documentos cargados en el índice."
                )
            
            docs_dict = {}
            for node in retrieved_nodes:
                doc_id = getattr(node.node, 'ref_doc_id', 'unknown')
                if doc_id not in docs_dict:
                    docs_dict[doc_id] = {
                        'id': doc_id,
                        'text': node.node.text,
                        'metadata': getattr(node.node, 'metadata', {})
                    }
                else:
                    # Concatenar texto si hay múltiples nodos del mismo documento
                    docs_dict[doc_id]['text'] += f"\n\n{node.node.text}"
            
            docs = list(docs_dict.values())

            if not docs:
                raise HTTPException(
                    status_code=404, 
                    detail="No se pudieron recuperar documentos del índice."
                )
            summaries = []
            query_engine = index.as_query_engine(
                text_qa_template=SUMMARIZE_PROMPT,
                similarity_top_k=5,  # Traer contexto relevante
                response_mode="tree_summarize"  # Mejor para resúmenes largos
            )
            for i, doc in enumerate(docs):
                try:
                    # Obtener el texto del documento
                    if hasattr(doc, 'text'):
                        doc_text = doc.text
                        doc_id = getattr(doc, 'id_', f'doc_{i}')
                    elif isinstance(doc, dict):
                        doc_text = doc.get('text', '')
                        doc_id = doc.get('id', f'doc_{i}')
                    else:
                        continue
                    
                    if not doc_text.strip():
                        continue
                    
                    # Crear una query específica para este documento
                    query = f"Resume el siguiente documento de manera estructurada y detallada: {doc_text[:1000]}..."
                    
                    summary_response = query_engine.query(query)
                    
                    # Obtener metadata si está disponible
                    metadata = {}
                    if hasattr(doc, 'metadata'):
                        metadata = doc.metadata
                    elif isinstance(doc, dict) and 'metadata' in doc:
                        metadata = doc['metadata']
                    
                    summary_data = {
                        "doc_id": doc_id,
                        "summary": str(summary_response),
                        "doc_length": len(doc_text),
                        "metadata": metadata
                    }
                    
                    summaries.append(summary_data)
                    
                except Exception as doc_error:
                    logging.error(f"Error procesando documento {i}: {str(doc_error)}")
                    continue
            
            if not summaries:
                raise HTTPException(
                    status_code=500, 
                    detail="No se pudieron generar resúmenes para ningún documento."
                )
            
            return summaries
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error general en summarize_docs: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al generar resúmenes: {str(e)}"
        )
     
def summarize_docs_alternative():
    """
    Método alternativo que recarga los documentos desde el directorio
    """
    try:

        # Si tienes acceso al directorio original de documentos
        documents_dir = UPLOAD_DIR # Cambia por tu directorio
        
        # Cargar documentos originales
        reader = SimpleDirectoryReader(documents_dir)
        documents = reader.load_data()
        
        if not documents:
            raise HTTPException(
                status_code=404, 
                detail="No hay documentos en el directorio."
            )
        
        docs_by_file = defaultdict(list)
        for doc in documents:
            filename = doc.metadata.get('file_name', 'unknown')
            base_filename = filename.replace('.pdf', '') if filename.endswith('.pdf') else filename
            docs_by_file[base_filename].append(doc)
        
        print(f"Archivos únicos encontrados: {list(docs_by_file.keys())}")
        
        
        # Crear índice temporal solo para resúmenes
        temp_index = VectorStoreIndex.from_documents(documents)
        
        summaries = []
        for filename, pages in docs_by_file.items():
            try:
                print(f"Procesando archivo: {filename} con {len(pages)} páginas")
                
                combined_text = ""
                total_chars = 0
                
                for page in pages:
                    page_text = page.text.strip()
                    if page_text:
                        combined_text += f"\n\n{page_text}"
                        total_chars += len(page_text)
                
                if not combined_text.strip():
                    print(f"Sin contenido para {filename}")
                    continue
                
                # Crear un documento combinado para este PDF
                combined_doc = Document(
                    text=combined_text,
                    metadata={
                        'file_name': filename,
                        'page_count': len(pages),
                        'total_characters': total_chars
                    }
                )
                
                # Crear índice temporal para este documento específico
                temp_index = VectorStoreIndex.from_documents([combined_doc])
                
                # Configurar query engine con el template corregido
                query_engine = temp_index.as_query_engine(
                    text_qa_template=SUMMARIZE_PROMPT,
                    similarity_top_k=3,
                    response_mode="compact"
                )
                
                # Query específica para este documento
                query = "Proporciona un resumen completo y estructurado de este documento PDF."
                summary = query_engine.query(query)
                
                summary_data = {
                    "doc_id": filename,
                    "filename": filename + ".pdf",
                    "summary": str(summary),
                    "page_count": len(pages),
                    "total_characters": total_chars,
                    "metadata": {
                        'file_name': filename + ".pdf",
                        'page_count': len(pages),
                        'processing_date': str(datetime.now())
                    }
                }
                
                summaries.append(summary_data)
                print(f"Resumen generado para {filename}")
                
            except Exception as doc_error:
                print(f"Error procesando {filename}: {str(doc_error)}")
                continue
        
        if not summaries:
            raise HTTPException(
                status_code=500,
                detail="No se pudieron generar resúmenes para ningún documento."
            )
        
        return summaries
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en método alternativo: {str(e)}"
        )
    
def summarize_from_existing_vectorstore():
    """
    Método que intenta usar tu vector store existente de manera más directa
    """
    try:
        vector_store = get_vector_store()
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, 
            persist_dir=PERSIST_DIR
        )
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, 
            storage_context=storage_context
        )
        
        # Crear retriever para obtener todos los nodos posibles
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=100  # Número alto
        )
        
        # Queries múltiples para capturar diferentes tipos de contenido
        queries = [
            "contenido documento texto información",
            "PDF archivo páginas contenido",
            "datos información principal tema",
            "resumen contenido principal documento"
        ]
        
        all_nodes = []
        for query in queries:
            nodes = retriever.retrieve(query)
            all_nodes.extend(nodes)
        
        if not all_nodes:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron nodos en el vector store"
            )
        
        # Agrupar nodos por documento fuente
        docs_by_source = defaultdict(list)
        for node in all_nodes:
            # Intentar obtener información del documento fuente
            source_info = "unknown"
            if hasattr(node.node, 'metadata') and node.node.metadata:
                source_info = node.node.metadata.get('file_name', 
                             node.node.metadata.get('source', 'unknown'))
            elif hasattr(node.node, 'ref_doc_id'):
                source_info = node.node.ref_doc_id
            
            docs_by_source[source_info].append(node.node.text)
        
        print(f"Documentos únicos encontrados: {list(docs_by_source.keys())}")
        
        summaries = []
        query_engine = index.as_query_engine(
            similarity_top_k=10,
            response_mode="tree_summarize"
        )
        
        for source, texts in docs_by_source.items():
            try:
                # Combinar textos del mismo documento
                combined_text = "\n\n".join(texts)
                
                if len(combined_text.strip()) < 50:  # Skip very short content
                    continue
                
                # Query para resumen
                query = f"""
                Crea un resumen estructurado del siguiente contenido de documento:
                
                Fuente: {source}
                
                Contenido: {combined_text[:3000]}...
                
                El resumen debe incluir:
                1. Tema principal
                2. Puntos clave (3-5 puntos)
                3. Información relevante
                4. Conclusiones si las hay
                
                Mantén el resumen entre 150-300 palabras.
                """
                
                summary = query_engine.query(query)
                
                summary_data = {
                    "doc_id": source,
                    "source": source,
                    "summary": str(summary),
                    "content_length": len(combined_text),
                    "chunks_count": len(texts)
                }
                
                summaries.append(summary_data)
                print(f"✅ Resumen generado para {source}")
                
            except Exception as doc_error:
                print(f"❌ Error procesando {source}: {str(doc_error)}")
                continue
        
        if not summaries:
            raise HTTPException(
                status_code=500,
                detail="No se pudieron generar resúmenes"
            )
        
        return summaries
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en summarize_from_existing_vectorstore: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando vector store: {str(e)}"
        )
    
def diagnose_index():
    """
    Función de diagnóstico para entender qué contiene tu índice
    """
    try:
        vector_store = get_vector_store()
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, 
            persist_dir=PERSIST_DIR
        )
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, 
            storage_context=storage_context
        )
        
        diagnosis = {
            "docstore_count": len(index.docstore.docs),
            "docstore_keys": list(index.docstore.docs.keys()),
            "vector_store_type": type(vector_store).__name__,
            "storage_context_exists": storage_context is not None
        }
        
        # Intentar recuperar algunos nodos
        retriever = VectorIndexRetriever(index=index, similarity_top_k=10)
        nodes = retriever.retrieve("test query")
        diagnosis["retrieved_nodes_count"] = len(nodes)
        diagnosis["node_types"] = [type(node.node).__name__ for node in nodes[:3]]
        
        return diagnosis
        
    except Exception as e:
        print(f"Error en index: {str(e)}")

# Función para analizar relaciones entre documentos
def analyze_document_relations(summaries):
    """
    Analiza las relaciones entre documentos basándose en sus resúmenes
    """
    try:
        
        if not summaries or len(summaries) < 2:
            return {
                "has_relations": False,
                "message": "Se necesitan al menos 2 documentos para analizar relaciones.",
                "total_docs": len(summaries) if summaries else 0
            }
        
        # Preparar información de los documentos para el análisis
        doc_info = []
        combined_text = ""
        for i, summary in enumerate(summaries, 1):
            doc_info.append(f"""
                DOCUMENTO {i}: {summary.get('filename', summary.get('doc_id', f'Documento {i}'))}
                RESUMEN: {summary.get('summary', 'Sin resumen disponible')}
                PÁGINAS: {summary.get('page_count', 'N/A')}
                ---""")
            combined_text += f"Documento {i}:\n\n{summary.get('filename', summary.get('doc_id', f'Documento {i}'))}"
            combined_text += f"\n\n{summary.get('summary', 'Sin resumen disponible')}"
            combined_text += "\n\n"
            combined_text += "-"*50
            combined_text += "\n\n"
        combined_doc = Document(text=combined_text)
        
        # documents_text = "\n".join(doc_info)
        temp_index = VectorStoreIndex.from_documents([combined_doc])
        query_engine = temp_index.as_query_engine(
                    text_qa_template=RELATION_PROMPT,
                    similarity_top_k=2,
                    response_mode="compact"
                )
        query = """
            Analiza las relaciones temáticas, temporales, de contenido y funcionales entre estos documentos.
            Incluye patrones, insights y conclusiones, sin inventar información que no esté en los resúmenes.
            """
        summary = query_engine.query(query)

        return str(summary)

    except Exception as doc_error:
        print(f"Error analizando relaciones: {str(doc_error)}")
