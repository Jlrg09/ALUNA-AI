"""
Servicio de reconocimiento visual para objetos culturales indígenas
Utiliza modelos de visión por computadora para identificar objetos típicos
de las culturas indígenas de la Sierra Nevada de Santa Marta
"""
import os
import io
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict, List, Tuple, Any
import torch
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionService:
    """Servicio para análisis visual de objetos culturales indígenas"""

    def __init__(self):
        """Inicializar el servicio de visión"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.blip_processor = None
        self.blip_model = None
        self.object_classifier = None
        self._initialize_models()

        # Base de conocimiento de objetos culturales
        self.cultural_objects = self._load_cultural_objects_database()

    def _initialize_models(self):
        """Inicializa los modelos de visión por computadora"""
        try:
            # Verificar si estamos en modo offline
            local_only = os.environ.get("HUGGINGFACE_HUB_OFFLINE", os.environ.get("HF_OFFLINE", "0")) in ("1", "true", "True")
            
            # Intentar cargar BLIP para descripción de imágenes
            try:
                from transformers import BlipProcessor, BlipForConditionalGeneration
                logger.info("Cargando modelo BLIP para descripción de imágenes...")
                
                self.blip_processor = BlipProcessor.from_pretrained(
                    "Salesforce/blip-image-captioning-base",
                    local_files_only=local_only,
                )
                self.blip_model = BlipForConditionalGeneration.from_pretrained(
                    "Salesforce/blip-image-captioning-base",
                    local_files_only=local_only,
                )
                self.blip_model.to(self.device)
                logger.info("Modelo BLIP cargado exitosamente")
                
            except Exception as e:
                logger.warning(f"No se pudo cargar BLIP: {e}")
                self.blip_processor = None
                self.blip_model = None

            # Intentar cargar pipeline para clasificación de objetos
            try:
                from transformers import pipeline
                logger.info("Cargando pipeline de clasificación de objetos...")
                
                self.object_classifier = pipeline(
                    "image-classification",
                    model="google/vit-base-patch16-224",
                    device=0 if self.device == "cuda" else -1,
                    local_files_only=local_only,
                )
                logger.info("Pipeline de clasificación cargado exitosamente")
                
            except Exception as e:
                logger.warning(f"No se pudo cargar el pipeline de clasificación: {e}")
                self.object_classifier = None

            # Verificar si al menos un modelo fue cargado
            if not any([self.blip_processor, self.blip_model, self.object_classifier]):
                logger.warning("Ningún modelo de visión fue cargado. Funcionalidad limitada.")
                
        except Exception as e:
            logger.error(f"Error inesperado inicializando modelos de visión: {e}")

    def _load_cultural_objects_database(self) -> Dict[str, Dict[str, Any]]:
        """Carga la base de datos de objetos culturales indígenas"""
        return {
            "mochila_arhuaca": {
                "name": "Mochila Arhuaca",
                "culture": "Arhuaco",
                "description": "Bolso tradicional tejido a mano por las mujeres arhuacas con fibras naturales como el fique o algodón. Cada diseño tiene significado espiritual y representa elementos de la cosmogonía arhuaca.",
                "keywords": ["bag", "woven", "textile", "colorful", "geometric", "traditional", "handbag", "mochila", "tejido"],
                "materials": ["fique", "algodón", "lana"],
                "significance": "Representa la conexión con la Madre Tierra y contiene los pensamientos y energías de quien la teje."
            },
            "poporo": {
                "name": "Poporo",
                "culture": "Kogui/Arhuaco",
                "description": "Recipiente sagrado utilizado por los hombres indígenas para guardar cal (mambe) que se consume con hojas de coca. Es un símbolo de masculinidad y sabiduría.",
                "keywords": ["gourd", "container", "vessel", "traditional", "sacred", "brown", "calabash", "poporo"],
                "materials": ["calabazo", "madera"],
                "significance": "Representa la matriz femenina y es fundamental en rituales espirituales y de paso a la adultez."
            },
            "tutuma": {
                "name": "Tutuma",
                "culture": "Kogui/Wiwa/Arhuaco",
                "description": "Recipiente elaborado del fruto del totumo, utilizado para transportar y almacenar agua, chicha u otros líquidos. Es fundamental en la vida cotidiana indígena.",
                "keywords": ["bowl", "gourd", "container", "vessel", "brown", "natural", "round", "tutuma"],
                "materials": ["totumo", "calabazo"],
                "significance": "Simboliza la abundancia y la conexión con los recursos naturales de la Sierra Nevada."
            },
            "sombrero_vueltiao": {
                "name": "Sombrero Vueltiao",
                "culture": "Zenú",
                "description": "Sombrero tradicional colombiano tejido en fibra de caña flecha. Aunque originario de la cultura Zenú, es ampliamente reconocido en toda la región Caribe.",
                "keywords": ["hat", "woven", "traditional", "beige", "straw", "Colombian", "circular", "vueltiao"],
                "materials": ["caña flecha"],
                "significance": "Símbolo nacional de Colombia y patrimonio cultural que representa la habilidad artesanal indígena."
            },
            "manta_arhuaca": {
                "name": "Manta Arhuaca",
                "culture": "Arhuaco",
                "description": "Vestimenta tradicional blanca usada tanto por hombres como mujeres arhuacas. Representa pureza y conexión espiritual con los ancestros.",
                "keywords": ["clothing", "white", "robe", "traditional", "dress", "garment", "manta"],
                "materials": ["algodón", "lana de oveja"],
                "significance": "Representa la pureza espiritual y la identidad cultural arhuaca."
            },
            "collar_chaquira": {
                "name": "Collar de Chaquira",
                "culture": "Arhuaco/Kogui",
                "description": "Collar elaborado con pequeñas cuentas de colores que forman patrones geométricos. Cada color y diseño tiene significado espiritual específico.",
                "keywords": ["necklace", "beads", "colorful", "jewelry", "geometric", "pattern", "chaquira"],
                "materials": ["chaquira", "mostacilla", "hilos"],
                "significance": "Protección espiritual y representación de elementos de la naturaleza y cosmogonía indígena."
            }
        }

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analiza una imagen para identificar objetos culturales indígenas

        Args:
            image_path: Ruta a la imagen a analizar

        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Cargar y procesar imagen
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return {"error": "No se pudo cargar la imagen"}

            # Análisis general de la imagen
            description = self._generate_image_description(image)
            objects_detected = self._classify_objects(image)

            # Identificación de objetos culturales
            cultural_matches = self._identify_cultural_objects(description, objects_detected)

            # Análisis de colores dominantes
            dominant_colors = self._analyze_dominant_colors(image_path)

            # Análisis de textura y patrones
            texture_analysis = self._analyze_texture_patterns(image_path)

            return {
                "description": description,
                "objects_detected": objects_detected,
                "cultural_objects": cultural_matches,
                "dominant_colors": dominant_colors,
                "texture_analysis": texture_analysis,
                "analysis_summary": self._generate_analysis_summary(cultural_matches, description),
                "confidence_score": self._calculate_overall_confidence(cultural_matches)
            }

        except Exception as e:
            logger.error(f"Error analizando imagen: {e}")
            return {"error": f"Error procesando imagen: {str(e)}"}

    def analyze_image_from_bytes(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Analiza una imagen desde bytes directamente

        Args:
            image_bytes: Bytes de la imagen
            filename: Nombre del archivo

        Returns:
            Diccionario con resultados del análisis
        """
        try:
            # Crear objeto Image desde bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Análisis general de la imagen
            description = self._generate_image_description(image)
            objects_detected = self._classify_objects(image)

            # Identificación de objetos culturales
            cultural_matches = self._identify_cultural_objects(description, objects_detected)

            # Para análisis que requieren archivo físico, crear temporal
            temp_path = self._create_temp_file(image_bytes, filename)
            
            dominant_colors = self._analyze_dominant_colors(temp_path) if temp_path else []
            texture_analysis = self._analyze_texture_patterns(temp_path) if temp_path else {}

            # Limpiar archivo temporal
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

            return {
                "filename": filename,
                "description": description,
                "objects_detected": objects_detected,
                "cultural_objects": cultural_matches,
                "dominant_colors": dominant_colors,
                "texture_analysis": texture_analysis,
                "analysis_summary": self._generate_analysis_summary(cultural_matches, description),
                "confidence_score": self._calculate_overall_confidence(cultural_matches)
            }

        except Exception as e:
            logger.error(f"Error analizando imagen desde bytes: {e}")
            return {"error": f"Error procesando imagen: {str(e)}"}

    def _load_and_preprocess_image(self, image_path: str) -> Optional[Image.Image]:
        """Carga y preprocesa una imagen"""
        try:
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                # Si es un objeto file-like
                image = Image.open(image_path)

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')

            return image

        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            return None

    def _generate_image_description(self, image: Image.Image) -> str:
        """Genera una descripción textual de la imagen usando BLIP"""
        try:
            if not self.blip_processor or not self.blip_model:
                return "Servicio de descripción de imágenes no disponible"
                
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.blip_model.generate(**inputs, max_length=50, num_beams=5)
            description = self.blip_processor.decode(output[0], skip_special_tokens=True)
            return description

        except Exception as e:
            logger.error(f"Error generando descripción: {e}")
            return "No se pudo generar descripción de la imagen"

    def _classify_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Clasifica objetos en la imagen"""
        try:
            if not self.object_classifier:
                return []
                
            results = self.object_classifier(image, top_k=5)
            return [{"label": result["label"], "confidence": result["score"]} for result in results]
            
        except Exception as e:
            logger.error(f"Error clasificando objetos: {e}")
            return []

    def _identify_cultural_objects(self, description: str, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica objetos culturales basado en la descripción y objetos detectados"""
        matches = []
        description_lower = description.lower()

        # Combinar labels de objetos detectados
        detected_labels = [obj["label"].lower() for obj in objects]
        all_text = f"{description_lower} {' '.join(detected_labels)}"

        for obj_id, obj_info in self.cultural_objects.items():
            confidence = 0
            matched_keywords = []

            # Buscar coincidencias con keywords
            for keyword in obj_info["keywords"]:
                if keyword.lower() in all_text:
                    confidence += 1
                    matched_keywords.append(keyword)

            # Calcular confianza normalizada
            if len(obj_info["keywords"]) > 0:
                confidence_score = confidence / len(obj_info["keywords"])

                if confidence_score > 0.2:  # Umbral mínimo de confianza
                    matches.append({
                        "object_id": obj_id,
                        "name": obj_info["name"],
                        "culture": obj_info["culture"],
                        "confidence": confidence_score,
                        "matched_keywords": matched_keywords,
                        "description": obj_info["description"],
                        "significance": obj_info["significance"],
                        "materials": obj_info["materials"]
                    })

        # Ordenar por confianza
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[:3]  # Retornar top 3 matches

    def _analyze_dominant_colors(self, image_path: str) -> List[Dict[str, Any]]:
        """Analiza los colores dominantes en la imagen"""
        try:
            # Cargar imagen con OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return []

            # Convertir de BGR a RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Redimensionar para acelerar el procesamiento
            image = cv2.resize(image, (150, 150))

            # Reshape para clustering
            data = image.reshape((-1, 3))
            data = np.float32(data)

            # K-means clustering para encontrar colores dominantes
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            k = 5
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Convertir centers a enteros y calcular porcentajes
            centers = np.uint8(centers)
            
            # Calcular frecuencia de cada color
            unique_labels, counts = np.unique(labels, return_counts=True)
            total_pixels = len(labels)
            
            color_info = []
            for i, center in enumerate(centers):
                if i in unique_labels:
                    idx = np.where(unique_labels == i)[0][0]
                    percentage = (counts[idx] / total_pixels) * 100
                    color_info.append({
                        "rgb": tuple(map(int, center)),
                        "hex": "#{:02x}{:02x}{:02x}".format(center[0], center[1], center[2]),
                        "percentage": round(percentage, 2)
                    })
            
            # Ordenar por porcentaje
            color_info.sort(key=lambda x: x["percentage"], reverse=True)
            return color_info

        except Exception as e:
            logger.error(f"Error analizando colores: {e}")
            return []

    def _analyze_texture_patterns(self, image_path: str) -> Dict[str, Any]:
        """Analiza texturas y patrones en la imagen"""
        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                return {}

            # Detectar bordes
            edges = cv2.Canny(image, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size

            # Detectar líneas (para patrones geométricos)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            line_count = len(lines) if lines is not None else 0

            # Análisis de textura usando filtros de Gabor
            texture_score = self._calculate_texture_score(image)

            return {
                "edge_density": round(edge_density, 3),
                "geometric_lines": line_count,
                "texture_complexity": texture_score,
                "pattern_type": self._classify_pattern_type(edge_density, line_count, texture_score)
            }

        except Exception as e:
            logger.error(f"Error analizando texturas: {e}")
            return {}

    def _calculate_texture_score(self, image: np.ndarray) -> float:
        """Calcula un score de complejidad de textura"""
        try:
            # Aplicar filtro Laplaciano para detectar texturas
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            texture_variance = laplacian.var()
            
            # Normalizar el score (valor típico entre 0-1000)
            normalized_score = min(texture_variance / 1000, 1.0)
            return round(normalized_score, 3)
            
        except Exception:
            return 0.0

    def _classify_pattern_type(self, edge_density: float, line_count: int, texture_score: float) -> str:
        """Clasifica el tipo de patrón basado en las métricas"""
        if line_count > 20 and edge_density > 0.1:
            return "geométrico"
        elif texture_score > 0.5:
            return "tejido_complejo"
        elif edge_density > 0.05:
            return "texturado"
        else:
            return "liso"

    def _generate_analysis_summary(self, cultural_matches: List[Dict[str, Any]], description: str) -> str:
        """Genera un resumen del análisis cultural"""
        if not cultural_matches:
            return f"Se detectó la imagen con la descripción: '{description}', pero no se identificaron objetos culturales indígenas específicos de la Sierra Nevada de Santa Marta."

        primary_match = cultural_matches[0]
        confidence_pct = int(primary_match['confidence'] * 100)
        
        summary = f"Se identificó posiblemente un {primary_match['name']} de la cultura {primary_match['culture']} con {confidence_pct}% de confianza. "
        summary += f"{primary_match['significance']}"

        if len(cultural_matches) > 1:
            other_matches = [match['name'] for match in cultural_matches[1:]]
            summary += f" También se detectaron similitudes con: {', '.join(other_matches)}."

        return summary

    def _calculate_overall_confidence(self, cultural_matches: List[Dict[str, Any]]) -> float:
        """Calcula la confianza general del análisis"""
        if not cultural_matches:
            return 0.0
        
        # Tomar la confianza del mejor match
        return round(cultural_matches[0]['confidence'], 3)

    def _create_temp_file(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """Crea un archivo temporal para análisis que lo requieren"""
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"vision_temp_{filename}")
            
            with open(temp_path, 'wb') as f:
                f.write(image_bytes)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error creando archivo temporal: {e}")
            return None

    def get_cultural_objects_info(self) -> Dict[str, Dict[str, Any]]:
        """Retorna información de todos los objetos culturales en la base de datos"""
        return self.cultural_objects

    def is_available(self) -> bool:
        """Verifica si el servicio de visión está disponible"""
        return any([self.blip_processor, self.blip_model, self.object_classifier])

    def get_service_status(self) -> Dict[str, bool]:
        """Retorna el estado de cada componente del servicio"""
        return {
            "blip_description_available": bool(self.blip_processor and self.blip_model),
            "object_classification_available": bool(self.object_classifier),
            "cultural_database_loaded": bool(self.cultural_objects),
            "opencv_available": True,  # Asumimos que OpenCV está disponible
            "overall_available": self.is_available()
        }