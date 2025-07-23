import os
import hashlib
import pickle
import re
from flask import request, jsonify
from PyPDF2 import PdfReader
import docx
import pytesseract
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import gc  # Para forzar limpieza de memoria

load_dotenv()

CARPETA = os.getenv("KNOWLEDGE_DIR", "documentos")
HASHES_FILE = os.path.join(CARPETA, "hashes.txt")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", os.path.join(CARPETA, "embeddings.pkl"))
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EXTENSIONES_VALIDAS = {".pdf", ".txt", ".docx"}

# Para sistemas Windows
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def limpiar_texto(texto):
    texto = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\xA1-\xFF]", "", texto)
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    return "\n".join(lineas)

def extraer_texto_pdf(path: str, ocr_min_chars=10) -> str:
    try:
        reader = PdfReader(path)
        texto = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        texto = limpiar_texto(texto)
        if len(texto) >= ocr_min_chars:
            return texto

        print(f"🔎 Aplicando OCR a: {os.path.basename(path)}")
        texto_ocr = ""

        # Procesamiento página por página para evitar cuelgues o truncamientos
        num_paginas = len(reader.pages)
        for i in range(num_paginas):
            images = convert_from_path(path, dpi=300, first_page=i+1, last_page=i+1)
            for image in images:
                contenido = pytesseract.image_to_string(image, lang='spa')
                contenido = limpiar_texto(contenido)
                texto_ocr += contenido + "\n"
            gc.collect()

        texto_ocr = limpiar_texto(texto_ocr)
        if len(texto_ocr) < ocr_min_chars:
            ocr_txt_path = path + ".ocr.txt"
            with open(ocr_txt_path, "w", encoding="utf-8") as f:
                f.write(texto_ocr)
            print(f"❌ OCR falló o el texto extraído es insuficiente: {os.path.basename(path)}. Guardado en {ocr_txt_path}")

        return texto_ocr
    except Exception as e:
        print(f"❌ Error en PDF (OCR incluido) {path}: {e}")
        return ""

def extraer_texto_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        return limpiar_texto("\n".join(p.text for p in doc.paragraphs))
    except Exception as e:
        print(f"❌ Error leyendo DOCX {path}: {e}")
        return ""

def extraer_texto(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extraer_texto_pdf(path)
    elif ext == ".docx":
        return extraer_texto_docx(path)
    elif ext == ".txt":
        try:
            with open(path, "r", encoding="utf-8") as f:
                return limpiar_texto(f.read())
        except Exception as e:
            print(f"❌ Error leyendo TXT {path}: {e}")
    return ""

def es_valido(path):
    return os.path.isfile(path) and os.path.splitext(path)[1].lower() in EXTENSIONES_VALIDAS

def calcular_hash_contenido(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def cargar_hashes_existentes():
    if not os.path.exists(HASHES_FILE):
        return set()
    with open(HASHES_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def guardar_hash(hash_str: str):
    with open(HASHES_FILE, "a", encoding="utf-8") as f:
        f.write(hash_str + "\n")

def generar_embeddings(docs):
    texts = [text for _, text in docs]
    try:
        doc_embeddings = EMBEDDING_MODEL.encode(texts, show_progress_bar=True)
        with open(EMBEDDINGS_FILE, "wb") as f:
            pickle.dump({
                "embeddings": doc_embeddings,
                "filenames": [fname for fname, _ in docs],
                "texts": texts
            }, f)
    except Exception as e:
        print(f"❌ Error generando embeddings: {e}")

def cargar_documentos_y_hashes():
    if not os.path.exists(CARPETA):
        return [], 0, 0, []

    hashes_existentes = cargar_hashes_existentes()
    docs = []
    nuevos = 0
    exist = 0
    errores = []

    for archivo in os.listdir(CARPETA):
        path = os.path.join(CARPETA, archivo)
        if not es_valido(path):
            continue

        texto = extraer_texto(path)
        if not texto or len(texto) < 30:
            errores.append(f"No se extrajo texto suficiente de: {archivo}")
            continue

        hash_actual = calcular_hash_contenido(texto)
        if hash_actual in hashes_existentes:
            exist += 1
            continue

        guardar_hash(hash_actual)
        docs.append((archivo, texto))
        nuevos += 1

    return docs, nuevos, exist, errores

def registrar_ruta_embeddings(app):
    @app.route("/api/embeddings/create", methods=["POST"])
    def crear_embeddings():
        docs, nuevos, existentes, errores = cargar_documentos_y_hashes()
        if docs:
            generar_embeddings(docs)
            msg = f"Embeddings generados para {nuevos} archivo(s) nuevo(s)."
        else:
            msg = "No hay archivos nuevos para procesar."

        return jsonify({
            "message": msg,
            "nuevos": nuevos,
            "existentes": existentes,
            "errores": errores
        })
