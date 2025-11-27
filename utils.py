"""
Utilidades comunes para el proyecto
"""
import os
import hashlib
from typing import Set
from config import KNOWLEDGE_DIR


class HashManager:
    """Gestor de hashes para control de cambios en documentos"""
    
    def __init__(self):
        self.hashes_file = os.path.join(KNOWLEDGE_DIR, "hashes.txt")
    
    def load_existing_hashes(self) -> Set[str]:
        """
        Carga hashes existentes desde archivo
        
        Returns:
            Set de hashes existentes
        """
        if not os.path.exists(self.hashes_file):
            return set()
        
        try:
            with open(self.hashes_file, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f.readlines() if line.strip())
        except Exception as e:
            print(f"❌ Error cargando hashes: {e}")
            return set()
    
    def save_hash(self, hash_str: str) -> None:
        """
        Guarda un hash en el archivo
        
        Args:
            hash_str: Hash a guardar
        """
        try:
            with open(self.hashes_file, "a", encoding="utf-8") as f:
                f.write(hash_str + "\n")
        except Exception as e:
            print(f"❌ Error guardando hash: {e}")
    
    def clear_hashes(self) -> bool:
        """
        Limpia el archivo de hashes
        
        Returns:
            True si se limpió exitosamente
        """
        try:
            if os.path.exists(self.hashes_file):
                os.remove(self.hashes_file)
            return True
        except Exception as e:
            print(f"❌ Error limpiando hashes: {e}")
            return False
    
    @staticmethod
    def calculate_content_hash(content: str) -> str:
        """
        Calcula hash MD5 del contenido
        
        Args:
            content: Contenido a hashear
            
        Returns:
            Hash MD5 del contenido
        """
        return hashlib.md5(content.encode("utf-8")).hexdigest()


class FileValidator:
    """Validador de archivos y imágenes"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB para imágenes
    
    @classmethod
    def is_valid_file(cls, filepath: str) -> bool:
        """
        Valida si un archivo es válido para procesamiento
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            True si el archivo es válido
        """
        if not os.path.isfile(filepath):
            return False
        
        # Verificar extensión
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS and ext not in cls.IMAGE_EXTENSIONS:
            return False
        
        # Verificar tamaño según tipo de archivo
        try:
            size = os.path.getsize(filepath)
            max_size = cls.MAX_IMAGE_SIZE if ext in cls.IMAGE_EXTENSIONS else cls.MAX_FILE_SIZE
            if size > max_size:
                file_type = "imagen" if ext in cls.IMAGE_EXTENSIONS else "archivo"
                print(f"⚠️ {file_type.capitalize()} muy grande: {filepath} ({size} bytes)")
                return False
        except Exception:
            return False
        
        return True
    
    @classmethod
    def allowed_file(cls, filename: str) -> bool:
        """
        Verifica si un nombre de archivo tiene extensión permitida (documentos o imágenes)
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si la extensión está permitida
        """
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        allowed_exts = {ext.lstrip('.') for ext in cls.ALLOWED_EXTENSIONS.union(cls.IMAGE_EXTENSIONS)}
        return ext in allowed_exts


class PathManager:
    """Gestor de rutas del proyecto"""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """
        Asegura que un directorio exista, creándolo si es necesario
        
        Args:
            directory: Ruta del directorio
            
        Returns:
            True si el directorio existe o se creó exitosamente
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error creando directorio {directory}: {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Convierte un nombre de archivo a uno seguro
        
        Args:
            filename: Nombre original del archivo
            
        Returns:
            Nombre de archivo seguro
        """
        # Remover caracteres peligrosos
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_ "
        safe_filename = "".join(c for c in filename if c in safe_chars)
        
        # Limitar longitud
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:255-len(ext)] + ext
        
        return safe_filename.strip()