# 🤖 AI Document Analyzer

Un agente de IA avanzado para análisis de documentos PDF que utiliza técnicas RAG (Retrieval-Augmented Generation) para proporcionar insights inteligentes y respuestas contextuales sobre tus documentos.

## 🚀 Características

- **Análisis Inteligente**: Realiza consultas en lenguaje natural sobre tus documentos
- **Resúmenes Automáticos**: Genera resúmenes completos y análisis de relaciones entre documentos
- **Vectorización Avanzada**: Utiliza embeddings para búsqueda semántica precisa
- **Múltiples Proveedores**: Soporte para OpenAI y Groq como proveedores de LLM
- **API RESTful**: Endpoints completos para gestión y consulta de documentos
- **Escalable**: Arquitectura basada en contenedores con Docker

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI
- **Vector Database**: Qdrant
- **RAG Framework**: LlamaIndex
- **LLM Providers**: OpenAI / Groq
- **Embeddings**: HuggingFace / OpenAI
- **Containerización**: Docker & Docker Compose

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- API Key de Groq o OpenAI
- Python 3.8+ (si ejecutas localmente)

## ⚡ Instalación Rápida

### 1. Clona el repositorio
```bash
git clone https://github.com/crcordova/rag-agent.git
cd rag-agent
```

### 2. Configura las variables de entorno
Copia el archivo de ejemplo y configúralo:
```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# QDRANT configs
QDRANT_PORT=6333
QDRANT_HOST=qdrant # usar 'localhost' si ejecutas localmente
USE_QDRANT=True

# LLM Configs
LLM_PROVIDER=groq # o 'openai'
GROQ_API_KEY=tu_groq_api_key_aqui
OPENAI_API_KEY=tu_openai_api_key_aqui
LLM_MODEL=llama3-8b-8192

# EMBEDDING config
EMBEDDING_PROVIDER=huggingface # o 'openai'
EMBEDDING_MODEL=hkunlp/instructor-base
DEVICE=cpu # o 'cuda' para uso con GPU

# Allowed origins (para CORS)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Inicia la aplicación
```bash
docker-compose up -d
```

¡Listo! Tu aplicación estará disponible en `http://localhost:8000`

## 🔧 Configuración Detallada

### Variables de Entorno

| Variable | Descripción | Valores Posibles | Por Defecto |
|----------|-------------|------------------|-------------|
| `QDRANT_HOST` | Host de Qdrant | `qdrant` (Docker) / `localhost` (local) | `qdrant` |
| `QDRANT_PORT` | Puerto de Qdrant | Cualquier puerto válido | `6333` |
| `LLM_PROVIDER` | Proveedor del modelo de lenguaje | `groq`, `openai` | `groq` |
| `GROQ_API_KEY` | API Key de Groq | Tu clave API de Groq | - |
| `OPENAI_API_KEY` | API Key de OpenAI | Tu clave API de OpenAI | - |
| `LLM_MODEL` | Modelo a utilizar | `llama3-8b-8192`, `gpt-3.5-turbo`, etc. | `llama3-8b-8192` |
| `EMBEDDING_PROVIDER` | Proveedor de embeddings | `huggingface`, `openai` | `huggingface` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `hkunlp/instructor-base`, etc. | `hkunlp/instructor-base` |
| `DEVICE` | Dispositivo para procesamiento | `cpu`, `cuda` | `cpu` |

### Obteniendo API Keys

**Para Groq:**
1. Visita [https://console.groq.com](https://console.groq.com)
2. Crea una cuenta o inicia sesión
3. Ve a API Keys y genera una nueva clave
4. Copia la clave que comienza con `gsk_`

**Para OpenAI:**
1. Visita [https://platform.openai.com](https://platform.openai.com)
2. Crea una cuenta o inicia sesión
3. Ve a API Keys y genera una nueva clave
4. Copia la clave que comienza con `sk-`

## 📚 Uso de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a la documentación interactiva en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints Principales

#### 📤 Gestión de Documentos

**Subir documentos PDF**
```bash
curl -X POST "http://localhost:8000/upload-pdf/" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@documento1.pdf" \
  -F "files=@documento2.pdf"
```

**Listar documentos cargados**
```bash
curl -X GET "http://localhost:8000/list-documents/"
```

**Reiniciar índice (eliminar todos los documentos)**
```bash
curl -X DELETE "http://localhost:8000/reset-index"
```

#### 🔍 Análisis y Consultas

**Consulta personalizada**
```bash
curl -X GET "http://localhost:8000/query?q=¿Cuáles son los puntos principales del documento?"
```

**Resumen completo de documentos**
```bash
curl -X GET "http://localhost:8000/summarize-docs"
```

**Resumen basado en vectores**
```bash
curl -X GET "http://localhost:8000/summarize-docs_byvector"
```

### Ejemplos de Consultas

- "¿Cuáles son los conceptos clave mencionados en los documentos?"
- "Resume las conclusiones principales"
- "¿Qué relación existe entre los documentos cargados?"
- "Encuentra información sobre [tema específico]"

## 🐳 Opciones de Despliegue

### Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### Ejecución Local (Desarrollo)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar Qdrant localmente
docker run -p 6333:6333 qdrant/qdrant

# Configurar QDRANT_HOST=localhost en .env

# Ejecutar la aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Solo Backend (Qdrant externo)
```bash
docker build -t rag-agent .
docker run -p 8000:8000 --env-file .env rag-agent
```

## 🔧 Solución de Problemas

### Problemas Comunes

**Error de conexión a Qdrant**
- Verifica que `QDRANT_HOST` esté configurado correctamente
- Si usas Docker: `QDRANT_HOST=qdrant`
- Si usas local: `QDRANT_HOST=localhost`

**Error de API Key**
- Verifica que la API Key esté correctamente configurada en `.env`
- Asegúrate de no tener espacios extra en la clave
- Verifica que la clave tenga los permisos necesarios

**Problemas de memoria/GPU**
- Para usar GPU, cambia `DEVICE=cuda` y asegúrate de tener CUDA instalado
- Si tienes problemas de memoria, usa modelos más pequeños

**Puerto ocupado**
- Cambia el puerto en `docker-compose.yml` si el puerto 8000 está ocupado
- Verifica que Qdrant no esté corriendo en otro puerto

### Logs y Debugging

```bash
# Ver logs de la aplicación
docker-compose logs -f backend

# Ver logs de Qdrant
docker-compose logs -f qdrant

# Ver estado de los contenedores
docker-compose ps
```

## 📝 Estructura del Proyecto

```
ai-document-analyzer/
├── app/
│   ├── main.py              # Aplicación principal FastAPI
│   ├── routers/             # Endpoints de la API
│   └── services/             # Lógica de negocio
├── documents/               # Carpeta para documentos PDF
├── docker-compose.yml       # Configuración Docker Compose
├── Dockerfile              # Imagen Docker del backend
├── requirements.txt        # Dependencias Python
├── .env.example           # Ejemplo de variables de entorno
└── README.md              # Este archivo
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Copyright **"All Rights Reserved"**

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Consulta la documentación de la API en `/docs`
3. Abre un issue en el repositorio
