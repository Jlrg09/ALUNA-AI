# ORIGEN - Versión Segura sin Filtros de Seguridad (antes ALUNA AI)

## Inicio Rápido

1) Instalar dependencias mínimas
```
pip install Flask python-dotenv
```

2) Ejecutar la aplicación
```
python -m examples.app_safe
```

3) Acceder a la interfaz
- Abrir navegador en: http://localhost:5000
- O usar la API directamente

## Archivos Principales

- examples/app_safe.py: Servidor Flask completo y seguro
- examples/config_simple.py: Configuración sin dependencias externas
- examples/simple_processor.py: Procesador de documentos sin ML
- examples/app_simple.py: Versión mínima básica
- tests/test_api.py: Pruebas de funcionalidad

## API Endpoints

- GET /api/status
- GET /api/documents
- POST /api/chat
- POST /api/search

Consulta el documento original para detalles completos y ejemplos de request.
