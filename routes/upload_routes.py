"""
Rutas para gestión de subida y procesamiento de archivos (movidas desde file_manager.py)
"""
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from utils import FileValidator, PathManager, HashManager
from rag.document_processor import DocumentProcessor
from rag.embedding_manager import EmbeddingManager
from config import KNOWLEDGE_DIR


class FileUploadManager:
    """Gestor de subida de archivos"""

    def __init__(self):
        self.validator = FileValidator()
        self.path_manager = PathManager()
        self.hash_manager = HashManager()
        self.doc_processor = DocumentProcessor()
        self.embedding_manager = EmbeddingManager()

        # Asegurar que el directorio de conocimiento existe
        self.path_manager.ensure_directory_exists(KNOWLEDGE_DIR)

    def save_uploaded_file(self, file: FileStorage) -> tuple[bool, str]:
        """
        Guarda un archivo subido

        Args:
            file: Archivo subido

        Returns:
            Tupla (éxito, mensaje)
        """
        if not file or file.filename == '':
            return False, "No se proporcionó ningún archivo"

        if not self.validator.allowed_file(file.filename):
            return False, f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(self.validator.ALLOWED_EXTENSIONS)}"

        # Generar nombre seguro
        filename = secure_filename(file.filename)
        if not filename:
            return False, "Nombre de archivo inválido"

        filepath = os.path.join(KNOWLEDGE_DIR, filename)

        try:
            # Guardar archivo
            file.save(filepath)

            # Verificar que el archivo se guardó correctamente
            if not os.path.exists(filepath):
                return False, "Error guardando el archivo"

            # Validar archivo guardado
            if not self.validator.is_valid_file(filepath):
                os.remove(filepath)  # Limpiar archivo inválido
                return False, "El archivo subido no es válido"

            return True, f"Archivo '{filename}' subido exitosamente"

        except Exception as e:
            # Limpiar archivo parcial si existe
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return False, f"Error subiendo archivo: {str(e)}"

    def process_and_update_embeddings(self) -> tuple[bool, str, dict]:
        """
        Procesa documentos y actualiza embeddings

        Returns:
            Tupla (éxito, mensaje, estadísticas)
        """
        try:
            # Cargar documentos
            documents = self.doc_processor.load_documents()

            if not documents:
                return False, "No se encontraron documentos para procesar", {}

            # Generar/actualizar embeddings
            embedding_data = self.embedding_manager.get_or_generate_embeddings(documents)

            if not embedding_data or len(embedding_data.embeddings) == 0:
                return False, "Error generando embeddings", {}

            stats = {
                "total_documents": len(documents),
                "embeddings_generated": len(embedding_data.embeddings),
                "files_processed": [doc.filename for doc in documents]
            }

            return True, "Embeddings actualizados exitosamente", stats

        except Exception as e:
            return False, f"Error procesando documentos: {str(e)}", {}
    
    def analyze_image_file(self, file: FileStorage) -> tuple[bool, str, dict]:
        """
        Analiza una imagen usando el servicio de visión
        
        Args:
            file: Archivo de imagen subido
            
        Returns:
            Tupla (éxito, mensaje, análisis)
        """
        if not file or file.filename == '':
            return False, "No se proporcionó ningún archivo", {}
        
        # Verificar que sea una imagen
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.validator.IMAGE_EXTENSIONS:
            return False, f"El archivo debe ser una imagen. Tipos permitidos: {', '.join(self.validator.IMAGE_EXTENSIONS)}", {}
        
        try:
            # Importar el servicio de visión
            from services.vision_service import VisionService
            vision_service = VisionService()
            
            # Leer los bytes del archivo
            file_bytes = file.read()
            file.stream.seek(0)  # Reset stream for potential future use
            
            # Analizar imagen
            analysis = vision_service.analyze_image_from_bytes(file_bytes, file.filename)
            
            if "error" in analysis:
                return False, f"Error analizando imagen: {analysis['error']}", {}
            
            return True, "Imagen analizada exitosamente", analysis
            
        except ImportError:
            return False, "Servicio de análisis de imágenes no disponible. Instale las dependencias necesarias.", {}
        except Exception as e:
            return False, f"Error analizando imagen: {str(e)}", {}
    
    def save_and_analyze_image(self, file: FileStorage) -> tuple[bool, str, dict]:
        """
        Guarda una imagen y la analiza
        
        Args:
            file: Archivo de imagen
            
        Returns:
            Tupla (éxito, mensaje, análisis)
        """
        # Primero guardar el archivo
        save_success, save_message = self.save_uploaded_file(file)
        
        if not save_success:
            return False, save_message, {}
        
        # Luego analizarlo
        analyze_success, analyze_message, analysis = self.analyze_image_file(file)
        
        if not analyze_success:
            return False, f"Archivo guardado pero {analyze_message}", {}
        
        return True, f"Imagen guardada y analizada exitosamente", analysis


def register_upload_routes(app):
    """
    Registra las rutas de subida de archivos

    Args:
        app: Instancia de Flask
    """
    upload_manager = FileUploadManager()

    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        """Endpoint para subir archivos"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No se encontró ningún archivo en la solicitud"}), 400

            file = request.files['file']

            # Guardar archivo
            success, message = upload_manager.save_uploaded_file(file)

            if not success:
                return jsonify({"error": message}), 400

            # Procesar y actualizar embeddings
            process_success, process_message, stats = upload_manager.process_and_update_embeddings()

            response_data = {
                "message": message,
                "processing_message": process_message,
                "processing_success": process_success
            }

            if stats:
                response_data["statistics"] = stats

            status_code = 200 if process_success else 206  # 206 = Partial Content
            return jsonify(response_data), status_code

        except Exception as e:
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

    @app.route("/api/upload/batch", methods=["POST"])
    def upload_multiple_files():
        """Endpoint para subir múltiples archivos"""
        try:
            if 'files' not in request.files:
                return jsonify({"error": "No se encontraron archivos en la solicitud"}), 400

            files = request.files.getlist('files')

            if not files or all(f.filename == '' for f in files):
                return jsonify({"error": "No se proporcionaron archivos válidos"}), 400

            results = []
            successful_uploads = 0

            # Procesar cada archivo
            for file in files:
                if file.filename == '':
                    continue

                success, message = upload_manager.save_uploaded_file(file)
                results.append({
                    "filename": file.filename,
                    "success": success,
                    "message": message
                })

                if success:
                    successful_uploads += 1

            # Solo actualizar embeddings si hubo subidas exitosas
            if successful_uploads > 0:
                process_success, process_message, stats = upload_manager.process_and_update_embeddings()
            else:
                process_success = False
                process_message = "No se subió ningún archivo exitosamente"
                stats = {}

            response_data = {
                "message": f"Procesados {len(results)} archivos, {successful_uploads} exitosos",
                "results": results,
                "processing_message": process_message,
                "processing_success": process_success
            }

            if stats:
                response_data["statistics"] = stats

            return jsonify(response_data), 200

        except Exception as e:
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    
    @app.route("/api/analyze-image", methods=["POST"])
    def analyze_image():
        """Endpoint para analizar imágenes sin guardarlas"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No se encontró ningún archivo en la solicitud"}), 400

            file = request.files['file']
            
            # Analizar imagen
            success, message, analysis = upload_manager.analyze_image_file(file)
            
            if not success:
                return jsonify({"error": message}), 400
            
            return jsonify({
                "message": message,
                "analysis": analysis
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    
    @app.route("/api/upload-and-analyze-image", methods=["POST"])
    def upload_and_analyze_image():
        """Endpoint para guardar y analizar imágenes"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No se encontró ningún archivo en la solicitud"}), 400

            file = request.files['file']
            
            # Guardar y analizar imagen
            success, message, analysis = upload_manager.save_and_analyze_image(file)
            
            if not success:
                return jsonify({"error": message}), 400
            
            # Procesar embeddings si la imagen se guardó
            if success:
                process_success, process_message, stats = upload_manager.process_and_update_embeddings()
            else:
                process_success = False
                process_message = "No se procesaron embeddings"
                stats = {}
            
            response_data = {
                "message": message,
                "analysis": analysis,
                "processing_message": process_message,
                "processing_success": process_success
            }
            
            if stats:
                response_data["statistics"] = stats
            
            return jsonify(response_data), 200
            
        except Exception as e:
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
