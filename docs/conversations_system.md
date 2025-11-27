# Sistema de Gestión de Conversaciones - ORIGEN

## Nuevas Funcionalidades Implementadas

### 1. **Conversaciones Dinámicas**
- Las conversaciones ya no están predefinidas en el HTML
- Se crean automáticamente cuando el usuario envía el primer mensaje
- Cada conversación tiene un ID único generado con UUID

### 2. **Títulos Automáticos**
- El título de cada conversación se genera automáticamente basándose en el primer mensaje del usuario
- Los títulos se truncan inteligentemente si son muy largos (máximo 50 caracteres)
- Se corta en palabras completas para mejor legibilidad

### 3. **Persistencia de Datos**
- Las conversaciones se guardan en el archivo `conversations/conversations.json`
- Cada conversación contiene:
  - ID único
  - Título generado automáticamente
  - Fecha de creación y última actualización
  - Historial completo de mensajes
  - Vista previa del primer mensaje

### 4. **Gestión Completa de Conversaciones**

#### Crear Nueva Conversación
```javascript
// El usuario hace clic en "Nueva conversación"
// Se crea automáticamente con título "Nueva conversación"
// Al enviar el primer mensaje, se genera el título real
```

#### Cargar Conversación Existente
```javascript
// El usuario hace clic en una conversación del sidebar
// Se cargan todos los mensajes y se muestra el historial completo
```

#### Eliminar Conversación
```javascript
// El usuario hace clic en el ícono de papelera
// Se confirma la acción antes de eliminar
// Si era la conversación activa, se inicia una nueva
```

#### Limpiar Conversación
```javascript
// El usuario hace clic en el botón de limpiar (escoba)
// Se eliminan todos los mensajes pero se mantiene la conversación
// El título se resetea a "Nueva conversación"
```

### 5. **API RESTful**

#### Endpoints Disponibles:

**GET /api/conversations/**
- Obtiene todas las conversaciones del usuario
- Query params: `limit` (default: 50)

**POST /api/conversations/**
- Crea una nueva conversación vacía

**GET /api/conversations/:id**
- Obtiene una conversación específica con todos sus mensajes

**POST /api/conversations/:id/messages**
- Agrega un mensaje a una conversación
- Body: `{ "type": "user|ai", "content": "mensaje" }`

**PUT /api/conversations/:id/title**
- Actualiza el título de una conversación manualmente
- Body: `{ "title": "Nuevo título" }`

**DELETE /api/conversations/:id**
- Elimina una conversación permanentemente

**POST /api/conversations/:id/clear**
- Limpia los mensajes de una conversación sin eliminarla

### 6. **Interfaz de Usuario Mejorada**

#### Sidebar
- Muestra todas las conversaciones ordenadas por fecha de actualización
- Indica la fecha de cada conversación de forma relativa:
  - "Hoy"
  - "Ayer"
  - "Hace X días"
  - "Hace X semanas"
  - Fecha específica para conversaciones más antiguas

- Botón de eliminar visible al hacer hover sobre cada conversación
- Conversación activa resaltada con fondo diferente

#### Header
- Título dinámico que cambia según la conversación activa
- Fecha de inicio de la conversación

### 7. **Flujo de Trabajo del Usuario**

1. **Inicio**: El usuario ve un sidebar vacío con el mensaje "Aún no tienes conversaciones"

2. **Primera Interacción**: 
   - El usuario escribe un mensaje
   - Se crea automáticamente una nueva conversación
   - El título se genera basándose en el primer mensaje
   - La conversación aparece en el sidebar

3. **Gestión de Conversaciones**:
   - El usuario puede cambiar entre conversaciones haciendo clic en ellas
   - Puede crear nuevas conversaciones con el botón "Nueva conversación"
   - Puede eliminar conversaciones que ya no necesita
   - Puede limpiar el contenido de una conversación

4. **Persistencia**:
   - Todas las conversaciones se guardan automáticamente
   - Al recargar la página, las conversaciones se cargan del servidor

### 8. **Estructura de Archivos**

```
ChatBot IguChat/
├── services/
│   └── conversation_manager.py    # Gestor de conversaciones (backend)
├── routes/
│   └── conversation_routes.py     # API endpoints para conversaciones
├── conversations/                  # Almacenamiento de conversaciones
│   ├── .gitignore                 # Ignora archivos JSON en git
│   └── conversations.json         # Base de datos de conversaciones
├── static/
│   └── js/
│       └── aluna_chat.js          # Lógica del frontend actualizada
└── templates/
    └── aluna_chat.html            # Plantilla HTML actualizada
```

### 9. **Características Técnicas**

- **Frontend**: JavaScript vanilla (sin frameworks)
- **Backend**: Flask con Python
- **Almacenamiento**: JSON (fácilmente migrable a base de datos)
- **IDs**: UUID v4 para identificadores únicos
- **Fechas**: ISO 8601 format para timestamps

### 10. **Próximas Mejoras Sugeridas**

- [ ] Búsqueda de conversaciones por título o contenido
- [ ] Renombrar conversaciones manualmente
- [ ] Exportar/importar conversaciones
- [ ] Archivar conversaciones antiguas
- [ ] Categorías o etiquetas para conversaciones
- [ ] Base de datos real (SQLite, PostgreSQL, MongoDB)
- [ ] Autenticación de usuarios (múltiples usuarios)
- [ ] Compartir conversaciones
- [ ] Resumen automático de conversaciones largas

### 11. **Cómo Usar**

1. Inicia el servidor Flask:
```bash
python app.py
```

2. Abre tu navegador en `http://localhost:5000`

3. Empieza a chatear - las conversaciones se crearán automáticamente

4. Gestiona tus conversaciones usando el sidebar

## Notas de Desarrollo

- Las conversaciones se guardan en `conversations/conversations.json`
- Este archivo se crea automáticamente si no existe
- El archivo está en `.gitignore` para no subir conversaciones personales a git
- El sistema es completamente funcional sin necesidad de base de datos
- Fácilmente escalable a múltiples usuarios con autenticación
