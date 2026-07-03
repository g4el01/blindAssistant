import os
import base64

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# =====================================================
# MODELOS
# =====================================================

class ImageRequest(BaseModel):
    image: str

# =====================================================
# FUNCIÓN GEMINI
# =====================================================

def analizar(imagen_b64, prompt):

    imagen_bytes = base64.b64decode(
        imagen_b64.split(",")[1]
    )

    respuesta = (
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=imagen_bytes,
                    mime_type="image/jpeg"
                ),
                prompt
            ]
        )
    )

    return respuesta.text

# =====================================================
# ENTORNO
# =====================================================

@app.post("/environment")

def environment(data: ImageRequest):

    prompt = """
Actúa como guía para una persona ciega.

Describe:

- obstáculos
- personas
- puertas
- escaleras
- objetos cercanos

Máximo 25 palabras.

Prioriza seguridad.
"""

    texto = analizar(
        data.image,
        prompt
    )

    return {
        "result": texto
    }

# =====================================================
# OCR
# =====================================================

@app.post("/ocr")

def ocr(data: ImageRequest):

    prompt = """
Lee todo el texto visible.

Incluye etiquetas.

Máximo 50 palabras.
"""

    texto = analizar(
        data.image,
        prompt
    )

    return {
        "result": texto
    }

# =====================================================
# DINERO
# =====================================================

@app.post("/money")

def money(data: ImageRequest):

    prompt = """
Identifica billetes y monedas.

Responde únicamente:

valor total y moneda.
"""

    texto = analizar(
        data.image,
        prompt
    )

    return {
        "result": texto
    }
    
# =====================================================
# FRONTEND
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="../frontend"),
    name="static"
)

@app.get("/")
async def home():
    return FileResponse("../frontend/index.html")
