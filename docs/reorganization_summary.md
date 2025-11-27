# Proyecto Reorganizado - ORIGEN (antes ALUNA AI)

## 📁 Estructura del Proyecto

```
ChatBot IguChat/
├── 📄 app.py                    # Aplicación principal Flask
├── 📄 config.py                 # Configuración centralizada (incluye ORIGEN_CONFIG)
├── 📄 models.py                 # Modelos de datos y tipos
├── 📄 utils.py                  # Utilidades comunes (HashManager, FileValidator, etc.)
├── 📄 file_manager.py           # Gestión de subida de archivos
├── 📄 requirements.txt          # Dependencias organizadas
│
├── 🗂️ rag/                      # Sistema RAG (Retrieval-Augmented Generation)
│   ├── context_search.py        # Búsqueda de contexto
│   ├── document_processor.py    # Procesamiento de documentos (mejorado)
│   └── embedding_manager.py     # Gestión de embeddings
│
├── 🗂️ routes/                   # Rutas de la aplicación web
│   ├── chat_routes.py          # Rutas de chat
│   └── aluna_routes.py         # Rutas de la interfaz ORIGEN (legacy path)
│
├── 🗂️ services/                 # Servicios de negocio
│   ├── chat_service.py         # Servicio de chat
│   └── prompt_builder.py       # Constructor de prompts
│
├── 🗂️ api/                      # Clientes de APIs externas
│   ├── google_ai_client.py     # Cliente Google AI
│   └── openrouter_client.py    # Cliente OpenRouter
│
├── 🗂️ templates/                # Plantillas HTML
│   └── aluna_chat.html         # Interfaz web de ORIGEN
│
├── 🗂️ static/                   # Archivos estáticos
│   ├── css/
│   └── js/
│
├── 🗂️ examples/                 # Ejemplos mínimos y seguros
│   ├── app_safe.py
│   ├── app_simple.py
│   ├── config_simple.py
│   └── simple_processor.py
│
├── 🗂️ scripts/                  # Scripts de mantenimiento/embeddings
│   ├── generate_embeddings.py
│   ├── process_documents.py
│   ├── reset_embeddings.py
│   └── verify_embeddings.py
│
├── 🗂️ tests/                    # Pruebas
│   ├── test_api.py
│   └── test_search.py
│
├── 🗂️ documentos/               # Base de conocimiento
│   └── [documentos PDF, TXT, DOCX]
│
└── 🗂️ tokens/                   # Tokens y sesiones
```

## 🧹 Archivos Eliminados (Duplicados/Obsoletos)

- ❌ `app_original_backup.py` - Backup obsoleto
- ❌ `aluna_config.py` - Integrado en `config.py`
- ❌ `procesar_carpeta.py` - Funcionalidad migrada a `rag/document_processor.py`
- ❌ `subir_archivos.py` - Funcionalidad migrada a `file_manager.py`
- ❌ `upload_knowledge.py` - Script simple eliminado
- ❌ `test_google_ai.py` - Archivo de prueba obsoleto
- ❌ `vistahtml.py` - Archivo obsoleto
- ❌ `chat_console.py` - Chat por consola no usado

## 🔧 Mejoras Implementadas

1. Configuración Centralizada en `config.py`
2. Procesamiento de Documentos Mejorado
3. Gestión de Archivos Organizada
4. Utilidades Comunes (`utils.py`)
5. Estructura Modular con separación de responsabilidades

## 🚀 Scripts de Utilidad

- `python scripts/generate_embeddings.py`
- `python scripts/process_documents.py`
- `python scripts/verify_embeddings.py`
- `python tests/test_search.py`

## 🎯 Beneficios de la Reorganización

1. Código más limpio (sin duplicaciones)
2. Mejor mantenimiento (modular)
3. Fácil extensión
4. Mejor rendimiento
5. Documentación clara

## 📝 Notas de Migración

- Las rutas de API siguen siendo las mismas
- Funcionalidad principal intacta
- Embeddings existentes compatibles
- Configuración puede requerir ajustes menores
