from llama_index.core.prompts import PromptTemplate

# SUMMARIZE_PROMPT = PromptTemplate("""
# Eres un asistente que resume documentos de manera objetiva.
# Para el documento proporcionado, entrega un resumen claro y conciso
# que capture las ideas principales. No inventes información que no esté presente.
# Devuelve el resumen en no más de 5 líneas.

# Documento:
# {document_text}

# Resumen:
# """)
SUMMARIZE_PROMPT = PromptTemplate("""
Eres un experto en análisis de documentos. Tu tarea es crear un resumen conciso y útil del siguiente documento.

Documento a resumir:
{context_str}

Instrucciones:
1. Identifica los puntos clave y temas principales del documento
2. Crea un resumen estructurado que incluya:
   - Tema principal del documento
   - Puntos clave (3-5 puntos máximo)
   - Conclusiones o información relevante
3. Mantén el resumen entre 150-300 palabras
4. Usa un lenguaje claro y profesional
5. Si el documento contiene datos específicos, inclúyelos en el resumen

Pregunta: Proporciona un resumen completo y estructurado de este documento.
""")

RELATION_PROMPT = PromptTemplate("""
Eres un experto analista de documentos. Tu tarea es identificar y analizar las relaciones, conexiones y patrones entre los siguientes documentos basándote en sus resúmenes.

DOCUMENTOS A ANALIZAR:
{context_str}

ANÁLISIS REQUERIDO:

1. **RELACIONES TEMÁTICAS**:
   - ¿Comparten temas principales o secundarios?
   - ¿Hay conceptos, términos o áreas de conocimiento comunes?
   - ¿Se complementan entre sí en algún tema específico?

2. **RELACIONES TEMPORALES**:
   - ¿Hay fechas, períodos o secuencias temporales relacionadas?
   - ¿Algunos documentos son continuación o actualización de otros?
   - ¿Existe alguna cronología entre los documentos?

3. **RELACIONES DE CONTENIDO**:
   - ¿Mencionan las mismas personas, organizaciones o entidades?
   - ¿Comparten datos, estadísticas o referencias similares?
   - ¿Hay contradicciones o información complementaria?

4. **RELACIONES FUNCIONALES**:
   - ¿Son del mismo tipo de documento (informes, manuales, estudios, etc.)?
   - ¿Pertenecen al mismo proyecto, área o departamento?

5. **PATRONES Y INSIGHTS**:
   - ¿Qué patrones generales emergen del conjunto de documentos?
   - ¿Hay alguna narrativa o historia completa cuando se ven juntos?
   - ¿Qué insights o conclusiones se pueden extraer del conjunto?

FORMATO DE RESPUESTA:
- Si NO hay relaciones significativas, explica por qué y menciona las diferencias principales
- Si SÍ hay relaciones, descríbelas de manera estructurada y específica
- Incluye ejemplos concretos de las conexiones encontradas
- Proporciona una conclusión sobre cómo estos documentos se relacionan como conjunto

RESPUESTA DETALLADA:
""")