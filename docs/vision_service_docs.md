# Servicio de Visión Computacional - ORIGEN

## Descripción General

El servicio de visión computacional de ORIGEN está diseñado específicamente para reconocer y analizar objetos culturales indígenas de la Sierra Nevada de Santa Marta. Utiliza modelos de inteligencia artificial avanzados para identificar elementos tradicionales de las culturas Arhuaca, Kogui, Wiwa y Zenú.

## Funcionalidades Implementadas

### ✅ Características Principales

1. **Descripción Automática de Imágenes**
   - Utiliza el modelo BLIP (Bootstrapped Language-Image Pre-training)
   - Genera descripciones textuales automáticas de las imágenes

2. **Clasificación de Objetos**
   - Emplea Vision Transformer (ViT) de Google
   - Identifica objetos generales en las imágenes

3. **Reconocimiento de Objetos Culturales**
   - Base de datos especializada con 6 objetos culturales clave:
     - Mochila Arhuaca
     - Poporo (Kogui/Arhuaco)
     - Tutuma (Kogui/Wiwa/Arhuaco)
     - Sombrero Vueltiao (Zenú)
     - Manta Arhuaca
     - Collar de Chaquira (Arhuaco/Kogui)

4. **Análisis de Colores Dominantes**
   - Clustering K-means para identificar paleta de colores
   - Cálculo de porcentajes de cada color
   - Conversión a formato RGB y hexadecimal

5. **Análisis de Texturas y Patrones**
   - Detección de bordes con algoritmo Canny
   - Identificación de líneas geométricas con transformada de Hough
   - Clasificación de tipos de patrón (geométrico, tejido complejo, texturado, liso)

6. **Sistema de Confianza**
   - Cálculo de scores de confianza para cada detección
   - Ranking de objetos culturales por probabilidad

### 🛠 Componentes Técnicos

#### Modelos de IA Utilizados:
- **BLIP**: `Salesforce/blip-image-captioning-base`
- **ViT**: `google/vit-base-patch16-224`

#### Bibliotecas Principales:
- `torch` y `transformers` para modelos de IA
- `opencv-python` para procesamiento de imágenes
- `PIL` para manipulación de imágenes
- `numpy` para operaciones numéricas

## Endpoints Disponibles

### 1. Análisis de Imagen
```
POST /api/vision/analyze
```

**Acepta:**
- Archivo de imagen (multipart/form-data)
- Imagen en base64 (JSON)

**Formatos soportados:** PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

**Respuesta ejemplo:**
```json
{
  "success": true,
  "analysis": {
    "description": "a colorful woven bag with geometric patterns",
    "objects_detected": [
      {"label": "handbag", "confidence": 0.85}
    ],
    "cultural_objects": [
      {
        "name": "Mochila Arhuaca",
        "culture": "Arhuaco",
        "confidence": 0.67,
        "significance": "Representa la conexión con la Madre Tierra..."
      }
    ],
    "dominant_colors": [
      {"rgb": [180, 45, 23], "hex": "#b42d17", "percentage": 35.2}
    ],
    "texture_analysis": {
      "pattern_type": "tejido_complejo",
      "edge_density": 0.15
    },
    "confidence_score": 0.67
  }
}
```

### 2. Estado del Servicio
```
GET /api/vision/status
```

**Respuesta:**
```json
{
  "service_status": {
    "blip_description_available": true,
    "object_classification_available": true,
    "cultural_database_loaded": true,
    "overall_available": true
  },
  "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"],
  "max_file_size_mb": 16
}
```

### 3. Base de Datos Cultural
```
GET /api/vision/cultural-objects
```

### 4. Prueba del Servicio
```
POST /api/vision/test
```

## Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install -r requirements_vision.txt
```

### 2. Configuración Opcional
Para modo offline (sin descargar modelos):
```bash
export HUGGINGFACE_HUB_OFFLINE=1
# o
export HF_OFFLINE=1
```

### 3. Verificar Instalación
```bash
python scripts/test_vision.py
```

## Integración con el Sistema Principal

### En DocumentProcessor
- Análisis automático de imágenes subidas
- Extracción de información cultural para indexación

### En Upload Routes
- Validación de imágenes
- Análisis en tiempo real durante la subida

### Manejo de Errores
- Modo degradado si los modelos no están disponibles
- Funcionamiento parcial con OpenCV únicamente
- Mensajes informativos sobre componentes faltantes

## Base de Datos de Objetos Culturales

### Estructura de Datos
Cada objeto incluye:
- **name**: Nombre del objeto
- **culture**: Cultura de origen
- **description**: Descripción detallada
- **keywords**: Palabras clave para detección
- **materials**: Materiales tradicionales
- **significance**: Significado cultural y espiritual

### Objetos Incluidos:

1. **Mochila Arhuaca** 🎒
   - Cultura: Arhuaco
   - Keywords: bag, woven, textile, colorful, geometric

2. **Poporo** 🥥
   - Cultura: Kogui/Arhuaco
   - Keywords: gourd, container, vessel, sacred

3. **Tutuma** 🥣
   - Cultura: Kogui/Wiwa/Arhuaco
   - Keywords: bowl, gourd, container, natural

4. **Sombrero Vueltiao** 👒
   - Cultura: Zenú
   - Keywords: hat, woven, traditional, straw

5. **Manta Arhuaca** 👕
   - Cultura: Arhuaco
   - Keywords: clothing, white, robe, traditional

6. **Collar de Chaquira** 📿
   - Cultura: Arhuaco/Kogui
   - Keywords: necklace, beads, colorful, jewelry

## Limitaciones y Consideraciones

### Limitaciones Actuales:
- Requiere modelos pre-entrenados (descarga inicial ~1-2GB)
- Funcionalidad limitada sin conexión a internet (primera vez)
- Base de datos cultural limitada a 6 objetos principales

### Mejoras Futuras Sugeridas:
- Expansión de la base de datos cultural
- Entrenamiento de modelos específicos para objetos indígenas
- Integración con APIs de museos y colecciones culturales
- Análisis de autenticidad y datación

## Monitoreo y Logs

El servicio genera logs detallados:
- Inicialización de modelos
- Errores de carga
- Análisis exitosos/fallidos
- Métricas de rendimiento

Para monitorear:
```python
import logging
logging.getLogger('services.vision_service').setLevel(logging.DEBUG)
```

## Escalabilidad

### Para Producción:
- Considerar usar GPU para mejor rendimiento
- Implementar cache de resultados
- Añadir límites de rate limiting
- Configurar CDN para modelos grandes

### Optimizaciones:
- Redimensionar imágenes antes del análisis
- Procesamiento asíncrono para imágenes grandes
- Paralelización de análisis múltiples