# IguiChat - Arquitectura Refactorizada

## Resumen de la Refactorización

Se ha dividido la lógica monolítica de `app.py` en múltiples módulos organizados para mejorar la escalabilidad, mantenibilidad y organización del código.

## Nueva Estructura

```
backend/
├── app.py                      # Aplicación principal simplificada
├── config.py                   # Configuración centralizada
├── models.py                   # Modelos de datos y tipos
├── api/                        # Clientes de APIs externas
│   ├── __init__.py
│   └── openrouter_client.py    # Cliente para OpenRouter API
├── rag/                        # Sistema RAG (Retrieval Augmented Generation)
│   ├── __init__.py
│   ├── document_processor.py   # Procesamiento de documentos
│   ├── embedding_manager.py    # Gestión de embeddings
│   └── context_search.py       # Búsqueda de contexto
├── services/                   # Servicios de negocio
│   ├── __init__.py
│   ├── prompt_builder.py       # Construcción de prompts
│   └── chat_service.py         # Servicio principal de chat
└── routes/                     # Endpoints de la API
	 ├── __init__.py
	 └── chat_routes.py           # Rutas del chat
```

## Componentes Principales

1. `config.py`
	- Propósito: Configuración centralizada
	- Contenido: Variables de entorno, constantes, configuraciones de APIs
	- Beneficios: Fácil modificación de configuraciones sin tocar lógica

2. `models.py`
	- Propósito: Definición de tipos y estructuras de datos
	- Contenido: Dataclasses, tipos personalizados, estructuras para serialización
	- Beneficios: Type safety, documentación clara de estructuras

3. `api/openrouter_client.py`
	- Propósito: Cliente para la API de OpenRouter
	- Responsabilidades: Autenticación, requests, manejo de errores, formateo de respuestas

4. `rag/document_processor.py`
	- Propósito: Procesamiento de documentos (PDF/TXT)
	- Responsabilidades: Carga, extracción de texto, validación

5. `rag/embedding_manager.py`
	- Propósito: Gestión de embeddings
	- Responsabilidades: Generación, persistencia, validación y modelo

6. `rag/context_search.py`
	- Propósito: Búsqueda de contexto relevante
	- Responsabilidades: Similitud coseno, filtrado, formateo

7. `services/prompt_builder.py`
	- Propósito: Construcción de prompts contextuales
	- Responsabilidades: Detección de temas, sugerencias, contexto

8. `services/chat_service.py`
	- Propósito: Servicio principal del chat
	- Responsabilidades: Orquestación, negocio, estado, health checks

9. `routes/chat_routes.py`
	- Propósito: Endpoints REST
	- Endpoints: POST /api/chat, GET /api/chat/health, POST /api/chat/reload

## Beneficios

- Escalabilidad: módulos especializados y reutilizables
- Mantenibilidad: separación de responsabilidades
- Testabilidad: componentes aislados, fácil mock
- Reutilización: APIs claras, bajo acoplamiento
- Configurabilidad: configuración centralizada
