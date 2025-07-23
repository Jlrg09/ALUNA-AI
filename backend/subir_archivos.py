import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import docx
import hashlib

# Configuración
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
UPLOAD_FOLDER = os.getenv("KNOWLEDGE_DIR", "documentos")
HASHES_FILE = os.path.join(UPLOAD_FOLDER, "hashes.txt")


# ------------------------
# FUNCIONES DE UTILIDAD
# ------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calcular_hash_contenido(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def cargar_hashes_existentes():
    if not os.path.exists(HASHES_FILE):
        return set()
    with open(HASHES_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def guardar_hash(hash_str: str):
    with open(HASHES_FILE, "a") as f:
        f.write(hash_str + "\n")

def extraer_texto_docx(filepath: str) -> str:
    try:
        doc = docx.Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"❌ Error leyendo DOCX {filepath}: {e}")
        return ""

def extraer_texto_pdf(filepath: str) -> str:
    try:
        reader = PdfReader(filepath)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        print(f"❌ Error leyendo PDF {filepath}: {e}")
        return ""

def extraer_texto_txt(filepath: str) -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error leyendo TXT {filepath}: {e}")
        return ""

def extraer_texto(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        return extraer_texto_pdf(filepath)
    elif filepath.endswith(".docx"):
        return extraer_texto_docx(filepath)
    elif filepath.endswith(".txt"):
        return extraer_texto_txt(filepath)
    return ""

# ------------------------
# ENDPOINT PARA SUBIR ARCHIVOS
# ------------------------
def registrar_ruta_upload(app):

    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"error": "No se encontró ningún archivo en la solicitud."}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "El nombre del archivo está vacío."}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Extraer texto y calcular hash
            texto = extraer_texto(filepath)
            if not texto.strip():
                os.remove(filepath)
                return jsonify({"error": "No se pudo extraer texto del archivo."}), 400

            hash_actual = calcular_hash_contenido(texto)
            hashes_previos = cargar_hashes_existentes()

            if hash_actual in hashes_previos:
                os.remove(filepath)
                return jsonify({"message": "Este archivo ya ha sido subido previamente."}), 200

            # Guardar hash si es nuevo
            guardar_hash(hash_actual)
            return jsonify({"message": f"Archivo '{filename}' subido y procesado exitosamente."}), 200

        return jsonify({"error": "Tipo de archivo no permitido."}), 400
