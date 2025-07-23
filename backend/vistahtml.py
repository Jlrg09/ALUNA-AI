import os
from flask import send_file, render_template_string

from procesar_carpeta import *

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vista OCR de Documentos</title>
    <style>
        body { font-family: Arial; padding: 2em; background: #f2f2f2; }
        h2 { margin-top: 2em; }
        pre { background: #fff; padding: 1em; border-radius: 5px; white-space: pre-wrap; }
        .archivo { margin-bottom: 2em; border-bottom: 1px solid #ccc; padding-bottom: 1em; }
    </style>
</head>
<body>
    <h1>📄 Vista de documentos OCR</h1>
    {% for doc in documentos %}
        <div class="archivo">
            <h2>{{ doc.nombre }}</h2>
            <p><strong>OCR:</strong> {{ "Sí" if doc.ocr else "No" }}</p>
            {% if doc.ocr_txt_path %}
                <p><a href="/api/ocr_txt/{{ doc.nombre }}">📥 Descargar archivo OCR (.ocr.txt)</a></p>
            {% endif %}
            <pre>{{ doc.texto[:3000] }}</pre>
        </div>
    {% endfor %}
</body>
</html>
"""

def registrar_ruta_ocr_vista(app):
    @app.route("/api/ocr_vista")
    def vista_ocr():
        documentos = []
        for archivo in os.listdir(CARPETA):
            path = os.path.join(CARPETA, archivo)
            if not es_valido(path):
                continue

            texto = extraer_texto(path)
            ocr_txt_path = path + ".ocr.txt"
            ocr_aplicado = os.path.exists(ocr_txt_path)

            if ocr_aplicado:
                try:
                    with open(ocr_txt_path, "r", encoding="utf-8") as f:
                        texto_ocr = f.read()
                        texto = texto_ocr or texto
                except:
                    pass

            documentos.append({
                "nombre": archivo,
                "ocr": ocr_aplicado,
                "texto": texto,
                "ocr_txt_path": ocr_txt_path if ocr_aplicado else None
            })

        return render_template_string(HTML_TEMPLATE, documentos=documentos)

    @app.route("/api/ocr_txt/<nombre>")
    def descargar_ocr_txt(nombre):
        path = os.path.join(CARPETA, nombre + ".ocr.txt")
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        return jsonify({"error": "Archivo OCR no encontrado"}), 404
