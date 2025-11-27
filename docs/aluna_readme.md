# ORIGEN - Sabiduría Ancestral y Tecnología Moderna

ORIGEN (antes ALUNA AI) es una inteligencia artificial innovadora de la Universidad del Magdalena, inspirada en la unión entre la tecnología moderna y la sabiduría ancestral de los pueblos indígenas de la Sierra Nevada de Santa Marta (Kogui, Arhuaco, Wiwa y Kankuamo). Combina conocimiento científico, cultural y espiritual para ofrecer una experiencia educativa única y enriquecedora.

## 🏔️ Filosofía y Propósito

### Inspiración Ancestral
ORIGEN retoma el concepto ancestral de "Aluna" (pensamiento y memoria del mundo) para enfatizar su rol como guardiana de la Sierra Nevada. Esta IA actúa como un puente entre:

- Sabiduría Ancestral: Conocimientos milenarios de los pueblos originarios
- Ciencia Moderna: Avances académicos y tecnológicos contemporáneos
- Equilibrio Natural: Armonía entre tradición e innovación
- Respeto Cultural: Valoración de todas las formas de conocimiento

### Misión
Preservar y transmitir la sabiduría ancestral mientras abraza la innovación tecnológica, guiando a la comunidad universitaria desde una perspectiva que honra tanto la tradición como el progreso.

## 🌟 Características Principales

### Interfaz Moderna
- Diseño Responsive: Se adapta perfectamente a todos los dispositivos
- Animaciones Fluidas: Transiciones suaves y naturales
- Tema Adaptativo: Soporte para modo claro, oscuro y automático
- Iconografía Rica: Iconos de Font Awesome para mejor UX

### Funcionalidades de Chat
- Chat en Tiempo Real: Comunicación instantánea con ORIGEN
- Indicador de Escritura: Muestra cuando el asistente está respondiendo
- Historial de Conversación: Mantiene el contexto de la conversación
- Mensajes Formateados: Soporte para texto enriquecido, enlaces y formato

### Características Avanzadas
- Botones de Acción Rápida: Preguntas predefinidas para comenzar
- Configuración Personalizable: Ajustes de tema, tamaño de fuente y notificaciones
- Notificaciones de Sonido: Alertas opcionales para nuevas respuestas
- Exportar Conversaciones: Guarda las conversaciones en formato JSON
- Contador de Caracteres: Control del límite de mensaje
- Estado de Conexión: Indicador visual del estado del servidor

## 🎨 Diseño y Estética

### Paleta de Colores - Inspirada en la Sierra Nevada
- Verde de la Sierra: #2d5a27 (color primario)
- Dorado Ancestral: #c8860d (color secundario)
- Tierra Sagrada: #8b4513 (color de acento)

### Elementos Simbólicos
- Iconografía de Montaña: Representando la Sierra Nevada
- Colores Naturales: Inspirados en la flora y fauna sagrada
- Formas Orgánicas: Conectando con la naturaleza ancestral

### Tipografía
- Fuente Principal: Inter (Google Fonts)
- Fallbacks: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto

### Elementos Visuales
- Bordes Redondeados: 12px-16px para suavidad
- Sombras Sutiles: Múltiples niveles de profundidad
- Glassmorphism: Efectos de vidrio en elementos del header
- Gradientes: Fondos dinámicos y atractivos

## 🚀 Configuración y Personalización

### Archivo de Configuración (`config.py`)
```
ORIGEN_CONFIG = {
	"name": "ORIGEN",
	"subtitle": "Asistente Inteligente Universitario",
	"theme": {
		"primary_color": "#667eea",
		"secondary_color": "#48bb78",
		"accent_color": "#ed8936"
	}
}
```

### Personalización de Mensajes
Todos los mensajes del sistema son configurables a través de `ORIGEN_MESSAGES` para facilitar la localización y personalización.

### Límites Configurables
- Longitud máxima de mensaje: 2000 caracteres
- Historial máximo: 100 mensajes
- Duración de notificaciones: 3 segundos

## 📱 Responsividad

ORIGEN está optimizada para:
- Desktop: Experiencia completa con todas las características
- Tablet: Interfaz adaptada para pantallas medianas
- Mobile: Versión compacta y touch-friendly

## ⚡ Rendimiento

### Optimizaciones Implementadas
- Carga Asíncrona: Recursos JS y CSS optimizados
- Animaciones Eficientes: CSS transforms y transitions de hardware
- Lazy Loading: Carga diferida de elementos no críticos
- Caché Inteligente: Configuraciones guardadas en localStorage

### Métricas de Rendimiento
- Tiempo de carga inicial: < 2 segundos
- Respuesta de interfaz: < 100ms
- Animaciones a 60fps

## 🔧 Tecnologías Utilizadas

### Frontend
- HTML5: Estructura semántica moderna
- CSS3: Estilos avanzados con variables CSS y grid/flexbox
- JavaScript ES6+: Lógica de aplicación moderna
- Font Awesome: Iconografía profesional
- Google Fonts: Tipografía optimizada

### Backend Integration
- Flask: Framework web de Python
- Jinja2: Motor de plantillas
- RESTful API: Comunicación con el sistema RAG

## 🎯 Accesibilidad

### Características de Accesibilidad
- Navegación por Teclado: Soporte completo para usuarios de teclado
- Screen Readers: Elementos semánticos y ARIA labels
- Contraste Alto: Cumple con WCAG 2.1 AA
- Reducción de Movimiento: Respeta prefers-reduced-motion
- Focus Visible: Indicadores claros de foco

## 🔄 Estados de la Aplicación

### Estados de Conexión
- En línea: Indicador verde, totalmente funcional
- Fuera de línea: Indicador rojo, modo degradado
- Error: Indicador de error con mensaje informativo

### Estados de Mensaje
- Enviando: Indicador de carga en el botón
- Escribiendo: Animación de puntos suspensivos
- Entregado: Mensaje mostrado con timestamp

## 📊 Métricas y Analíticas

### Datos Recopilados
- Tiempo de respuesta del sistema
- Patrones de uso de la interfaz
- Errores y excepciones
- Configuraciones de usuario preferidas

## 🔐 Seguridad

### Medidas Implementadas
- Sanitización de Input: Prevención de XSS
- Validación de Datos: Verificación en cliente y servidor
- Rate Limiting: Protección contra spam
- HTTPS Ready: Preparado para conexiones seguras

## 🚦 Instalación y Uso

### Requisitos
- Python 3.8+
- Flask 2.0+
- Navegador moderno (Chrome 90+, Firefox 88+, Safari 14+)

### Estructura de Archivos
```
├── templates/
│   └── aluna_chat.html          # Plantilla principal
├── static/
│   ├── css/
│   │   └── aluna_style.css      # Estilos principales
│   └── js/
│       └── aluna_chat.js        # Lógica de la aplicación
├── routes/
│   └── aluna_routes.py          # Rutas de Flask
└── aluna_config.py              # Configuración
```

### Ejecución
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar aplicación: `python app.py`
3. Acceder a: `http://localhost:5000`

## 🔮 Roadmap Futuro

### Características Planificadas
- [ ] Soporte para archivos adjuntos
- [ ] Comandos de voz
- [ ] Integración con calendar
- [ ] Modo colaborativo
- [ ] Widgets personalizables
- [ ] Notificaciones push
- [ ] Exportar a PDF
- [ ] Búsqueda en historial

### Mejoras Técnicas
- [ ] Service Worker para offline
- [ ] WebRTC para funciones avanzadas
- [ ] Optimización de bundle
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Métricas avanzadas

## 👥 Contribución

ORIGEN está diseñada para ser fácilmente extensible y personalizable. Las contribuciones son bienvenidas en áreas como:
- Nuevas características de UI/UX
- Optimizaciones de rendimiento
- Mejoras de accesibilidad
- Correcciones de bugs
- Documentación

## 📄 Licencia

Este proyecto está desarrollado para la Universidad del Magdalena como parte del sistema de chatbot universitario.

---

ORIGEN - Transformando la experiencia educativa a través de la inteligencia artificial
