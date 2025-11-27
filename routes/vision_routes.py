"""
Rutas para el servicio de visión computacional
Permite analizar imágenes de objetos culturales indígenas
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from services.vision_service import VisionService

vision_bp = Blueprint('vision', __name__)

# Configuración
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_image_file(filename):
    """Verifica si el archivo es una imagen válida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@vision_bp.route('/api/vision/analyze', methods=['POST'])
def analyze_image():
    """
    Analiza una imagen para identificar objetos culturales indígenas
    
    Acepta:
    - Archivo de imagen en multipart/form-data
    - JSON con imagen en base64
    
    Returns:
    - Análisis completo de la imagen incluyendo objetos culturales detectados
    """
    try:
        vision_service = VisionService()
        
        if not vision_service.is_available():
            return jsonify({
                "error": "Servicio de visión no disponible",
                "status": vision_service.get_service_status()
            }), 503
        
        # Verificar si hay archivo en la solicitud
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"error": "No se seleccionó ningún archivo"}), 400
            
            if file and allowed_image_file(file.filename):
                # Verificar tamaño del archivo
                file_bytes = file.read()
                if len(file_bytes) > MAX_FILE_SIZE:
                    return jsonify({"error": "Archivo demasiado grande (máximo 16MB)"}), 400
                
                # Analizar imagen desde bytes
                result = vision_service.analyze_image_from_bytes(file_bytes, file.filename)
                
                if "error" in result:
                    return jsonify(result), 500
                
                return jsonify({
                    "success": True,
                    "analysis": result
                })
            else:
                return jsonify({"error": "Tipo de archivo no permitido"}), 400
        
        # Verificar si hay datos JSON con imagen en base64
        elif request.is_json:
            data = request.get_json()
            
            if 'image_base64' not in data:
                return jsonify({"error": "Se requiere 'image_base64' en el JSON"}), 400
            
            import base64
            try:
                # Decodificar imagen base64
                image_data = data['image_base64']
                if ',' in image_data:
                    # Remover prefijo data:image/...;base64,
                    image_data = image_data.split(',')[1]
                
                file_bytes = base64.b64decode(image_data)
                filename = data.get('filename', 'image_base64.jpg')
                
                # Verificar tamaño
                if len(file_bytes) > MAX_FILE_SIZE:
                    return jsonify({"error": "Imagen demasiado grande (máximo 16MB)"}), 400
                
                # Analizar imagen
                result = vision_service.analyze_image_from_bytes(file_bytes, filename)
                
                if "error" in result:
                    return jsonify(result), 500
                
                return jsonify({
                    "success": True,
                    "analysis": result
                })
                
            except Exception as e:
                return jsonify({"error": f"Error decodificando imagen base64: {str(e)}"}), 400
        
        else:
            return jsonify({
                "error": "Se requiere un archivo de imagen o imagen en base64"
            }), 400
    
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@vision_bp.route('/api/vision/status', methods=['GET'])
def get_vision_status():
    """
    Obtiene el estado del servicio de visión
    
    Returns:
    - Estado de cada componente del servicio
    """
    try:
        vision_service = VisionService()
        status = vision_service.get_service_status()
        
        return jsonify({
            "service_status": status,
            "available": vision_service.is_available(),
            "supported_formats": list(ALLOWED_IMAGE_EXTENSIONS),
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
        })
    
    except Exception as e:
        return jsonify({"error": f"Error obteniendo estado: {str(e)}"}), 500

@vision_bp.route('/api/vision/cultural-objects', methods=['GET'])
def get_cultural_objects():
    """
    Obtiene información de todos los objetos culturales en la base de datos
    
    Returns:
    - Diccionario con información de objetos culturales indígenas
    """
    try:
        vision_service = VisionService()
        objects_info = vision_service.get_cultural_objects_info()
        
        return jsonify({
            "cultural_objects": objects_info,
            "total_objects": len(objects_info)
        })
    
    except Exception as e:
        return jsonify({"error": f"Error obteniendo objetos culturales: {str(e)}"}), 500

@vision_bp.route('/api/vision/test', methods=['POST'])
def test_vision_service():
    """
    Endpoint de prueba para el servicio de visión
    Útil para verificar que todo funciona correctamente
    """
    try:
        vision_service = VisionService()
        
        # Crear una imagen de prueba simple
        from PIL import Image
        import io
        
        # Crear imagen de prueba 100x100 azul
        test_image = Image.new('RGB', (100, 100), color='blue')
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Analizar imagen de prueba
        result = vision_service.analyze_image_from_bytes(img_byte_arr, "test_image.png")
        
        return jsonify({
            "test_successful": "error" not in result,
            "service_available": vision_service.is_available(),
            "test_result": result
        })
    
    except Exception as e:
        return jsonify({
            "test_successful": False,
            "error": f"Error en prueba: {str(e)}"
        }), 500