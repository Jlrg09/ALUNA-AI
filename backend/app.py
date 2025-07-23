import os
import json
import requests
from flask import Flask, request, jsonify
from typing import List, Tuple
from dotenv import load_dotenv
from procesar_carpeta import registrar_ruta_embeddings
from subir_archivos import registrar_ruta_upload
from sentence_transformers import SentenceTransformer
from reset_embeddings import registrar_ruta_reset
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader
import pickle
from vistahtml import registrar_ruta_ocr_vista  # cambia por el nombre real del archivo


load_dotenv()
app = Flask(__name__)

# ------------------------
# CONFIGURACIÓN
# ------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", "")

BOT_NAME = "Igüi AI la iguana intercultural"
WELCOME_TEXT = "IGÜI*AI*"
UNIVERSIDAD = "Universidad del Magdalena"

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


DEPENDENCIAS = {
    "admisiones": "Oficina de Admisiones y Registro Académico",
    "matrícula": "Oficina de Admisiones y Registro Académico",
    "becas": "Oficina de Bienestar Universitario",
    "psicológico": "Oficina de Bienestar Universitario",
    "deportes": "Oficina de Deportes",
    "pagos": "Tesorería",
    "financiera": "Tesorería",
    "internacional": "Oficina de Relaciones Internacionales",
    "carnet": "Oficina de Bienestar Universitario",
    "syste+/systeplus": ""
}

# ------------------------
# UTILIDADES RAG
# ------------------------
def extraer_texto_pdf(path):
    try:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"❌ Error leyendo PDF {path}: {e}")
        return ""

def cargar_documentos() -> List[Tuple[str, str]]:
    docs = []
    if not os.path.exists(KNOWLEDGE_DIR):
        return docs
    for fname in os.listdir(KNOWLEDGE_DIR):
        fpath = os.path.join(KNOWLEDGE_DIR, fname)
        if fname.endswith(".txt"):
            try:
                with open(fpath, encoding="utf-8") as f:
                    docs.append((fname, f.read()))
            except Exception as e:
                print(f"❌ Error leyendo {fname}: {e}")
        elif fname.endswith(".pdf"):
            contenido = extraer_texto_pdf(fpath)
            if contenido:
                docs.append((fname, contenido))
    return docs

def guardar_embeddings(embeddings):
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(embeddings, f)

def cargar_embeddings():
    if not os.path.exists(EMBEDDINGS_FILE):
        return None
    with open(EMBEDDINGS_FILE, "rb") as f:
        return pickle.load(f)

def generar_embeddings(docs: List[Tuple[str, str]]):
    texts = [text for _, text in docs]
    try:
        doc_embeddings = EMBEDDING_MODEL.encode(texts, show_progress_bar=True)
        guardar_embeddings({
            "embeddings": doc_embeddings,
            "filenames": [fname for fname, _ in docs],
            "texts": texts
        })
    except Exception as e:
        print(f"❌ Error generando embeddings: {e}")

def buscar_contexto(pregunta: str, docs: List[Tuple[str, str]], top_k: int = 3) -> str:
    emb_data = cargar_embeddings()
    if not docs or emb_data is None or len(emb_data["texts"]) != len(docs):
        generar_embeddings(docs)
        emb_data = cargar_embeddings()
    
    doc_embeddings = emb_data["embeddings"]
    texts = emb_data["texts"]
    pregunta_embedding = EMBEDDING_MODEL.encode([pregunta])
    sims = cosine_similarity(pregunta_embedding, doc_embeddings)[0]
    
    top_indices = sims.argsort()[-top_k:][::-1]
    contexto = "\n\n".join(
        f"[Fragmento Relevante {i+1} - Similitud {sims[idx]:.2f}]:\n{texts[idx]}"
        for i, idx in enumerate(top_indices) if sims[idx] > 0.3
    )
    return contexto

def sugerir_dependencia(pregunta: str) -> str:
    pregunta_lower = pregunta.lower()
    for clave in DEPENDENCIAS:
        if clave in pregunta_lower:
            return DEPENDENCIAS[clave]
    return "la dependencia correspondiente (por favor especifica tu consulta para orientarte mejor)"

def armar_prompt(pregunta: str, contexto: str, dependencia: str, sin_contexto: bool, no_universidad: bool) -> str:
    prompt = (
        f"Eres {BOT_NAME}, el asistente virtual institucional de la {UNIVERSIDAD}, llamado IguiChat. "
        f"Responde preguntas de manera clara, precisa, breve y académica, basándote en los documentos institucionales. "
        f"Evita adornos como asteriscos, numerales o viñetas. Si citas una norma, menciona el artículo o parágrafo correspondiente.\n\n"
        #f"Si la pregunta no está relacionada con la universidad, responde amablemente, mostrando empatía, y aclara que solo puedes ayudar en temas institucionales.\n\n"
        f"Si la información no está en tu base, responde que no tienes información suficiente y sugiere consultar a {dependencia}. No inventes respuestas ni des información incorrecta.\n"
    )
    if contexto:
        prompt += f"\nInformación útil para responder:\n{contexto}\n"
    prompt += f"\nPregunta del usuario: {pregunta}\n"
    if sin_contexto:
        prompt += f"\nNo tienes información suficiente para responder de manera precisa.\n"
    if no_universidad:
        prompt += f"\nLa pregunta no es sobre la universidad, pero responde de manera amable.\n"
    prompt += f"\nResponde ahora:"
    return prompt

# ------------------------
# OPENROUTER
# ------------------------
def consulta_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": f"Eres {BOT_NAME}, un chatbot institucional de la {UNIVERSIDAD}. Responde solo sobre temas relacionados con esta universidad. Sé breve y directo. Si no tienes información suficiente, sugiere a qué dependencia consultar."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.3  
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.ok:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print("❌ OpenRouter Error:", response.text)
            return "Lo siento, no pude procesar tu pregunta en este momento."
    except Exception as e:
        print("❌ OpenRouter Exception:", e)
        return "Lo siento, ocurrió un error técnico."

# ------------------------
# ENDPOINTS
# ------------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    pregunta = data.get("question", "").strip()
    if not pregunta:
        return jsonify({"answer": "Por favor, escribe tu pregunta."})

    docs = cargar_documentos()
    contexto = buscar_contexto(pregunta, docs)
    sin_contexto = not bool(contexto)
    no_universidad = False

    # Lógica simple para detectar si la pregunta es sobre la universidad
    if all(keyword not in pregunta.lower() for keyword in ["universidad", "unimagdalena", "estudiante", "carrera", "programa", "docente", "profesor", "materia", "facultad", "admisión", "matrícula", "grado"]):
        no_universidad = True

    dependencia = sugerir_dependencia(pregunta) if sin_contexto else ""

    prompt = armar_prompt(pregunta, contexto, dependencia, sin_contexto, no_universidad)
    respuesta = consulta_openrouter(prompt)
    respuesta_final = f"{WELCOME_TEXT}\n{respuesta.strip()}"
    return jsonify({"answer": respuesta_final})

# ------------------------
# INICIAR APP
# ------------------------
if __name__ == "__main__":
    registrar_ruta_upload(app)
    registrar_ruta_reset(app)
    registrar_ruta_embeddings(app)
    registrar_ruta_ocr_vista(app)
    app.run(port=5000, host="0.0.0.0", debug=True)
    