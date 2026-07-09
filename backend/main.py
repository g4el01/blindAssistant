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
            model="gemini-3.1-flash-lite",
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
No uses introducciones, saludos ni frases como "En la imagen veo...". Ve directo a los datos críticos usando la estructura de las "3 D": Dirección, Distancia y Descripción.

Sigue estrictamente este orden de prioridad en tu respuesta:

1. ALERTAS INMEDIATAS (A menos de 2 metros): Si hay un peligro inminente en el suelo o a la altura de la cabeza, dilo PRIMERO y con urgencia.
   - Ejemplos: "Cuidado, escalón hacia abajo a un paso", "Rama baja al frente", "Bache profundo a la derecha".

2. OBSTÁCULOS EN LA RUTA (A más de 2 metros): Describe objetos que bloqueen el paso recto.
   - Ejemplos: "Contenedor de basura al frente a unos 4 metros", "Poste de luz adelante a la izquierda".

3. DINÁMICA DEL ENTORNO (Gente o vehículos en movimiento):
   - Ejemplos: "Personas caminando hacia ti", "Un auto saliendo de una cochera a tu derecha".

4. RUTA SUGERIDA: Dale una indicación clara de por dónde continuar si el frente está bloqueado.
   - Ejemplos: "Camino despejado hacia la izquierda", "La banqueta continúa libre por el centro".

REGLAS CRÍTICAS DE REDACCIÓN:
- Sé extremadamente breve (máximo 2 o 3 frases cortas). El usuario está caminando y necesita procesar la información rápido.
- Usa referencias espaciales claras basadas en el cuerpo del usuario: "Al frente", "A tu izquierda", "A tu derecha", "A la altura de la cabeza".
- No describas estética (colores de edificios, modelos de autos, estética de la ropa). Solo describe lo que afecte el paso.

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
No saludes ni uses introducciones. Ve directo a la información siguiendo estas reglas según el escenario detectado:

[ESCENARIO 1: DOCUMENTOS O LIBROS]
- Si es una página de texto continuo, transcríbela textualmente respetando párrafos.
- Omite números de página o encabezados repetitivos que interrumpan la lectura.

[ESCENARIO 2: EMPAQUES, MEDICAMENTOS O ALIMENTOS]
- Identifica primero el producto. Ejemplo: "Caja de leche Santa Clara".
- Busca y lee directamente la información crítica: Fecha de caducidad, instrucciones de uso o advertencias de alérgenos. No leas todo el diseño de marketing a menos que falte lo anterior.

[ESCENARIO 3: LETREROS, CALLES O SEÑALÉTICA]
- Sé ultra breve. Di el tipo de letrero y lo que dice. Ejemplo: "Letrero de calle: Avenida Juárez" o "Cartel: Baño de hombres".

[ESCENARIO 4: INFORMACIÓN EN PANTALLAS (Cajeros, Monitores, Celulares)]
- Transcribe solo las opciones disponibles o el mensaje de error en pantalla. Ejemplo: "Pantalla de cajero: Seleccione su operación. Retiro de efectivo, Consulta de saldo...".

[REGLAS GENERALES CRÍTICAS]
1. Si el texto está incompleto o cortado, avisa: "Texto incompleto por los lados, dice: [texto]".
2. Si la imagen está borrosa o no hay texto, di únicamente: "Texto no legible" o "No se detecta texto".
3. Usa un tono neutral, descriptivo y directo. No describas colores ni logotipos a menos que definan la marca del producto.

trata de no usar tantas palabras si es posible.
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
Actúa como un detector de divisas de alta precisión para una persona con discapacidad visual. Tu única tarea es identificar los billetes y monedas visibles en la imagen. La precisión es crítica para la seguridad financiera del usuario.

Sigue estrictamente estas reglas:
1. RESPUESTA INMEDIATA Y DIRECTA: Ve directo al grano. NO uses introducciones como "Veo un billete de..." o "En tu mano tienes...". Di la cantidad y la moneda inmediatamente.
2. FORMATO DE CONTEO:
   - Si es un solo billete/moneda: Di el valor y la moneda. (Ej: "20 euros" o "100 pesos mexicanos").
   - Si hay varios billetes/monedas: Di el total acumulado primero y luego el desglose. (Ej: "En total hay 70 dólares. Un billete de 50 y uno de 20").
3. ADVERTENCIA DE INCERTIDUMBRE: Si el billete está muy doblado, tapado por los dedos, la luz es mala o tienes la más mínima duda de su valor, NO adivines. Di claramente: "No puedo identificar el valor con certeza. Por favor, desdobla el billete o muévelo un poco".
4. DETECCIÓN DE REVERSO/ANVERSO: Si el billete está por el lado que no muestra el número claramente pero reconoces el diseño, confirma el valor de todos modos.
5. SI NO ES DINERO: Si en la imagen no hay billetes ni monedas, di textualmente: "No se detecta dinero en la imagen".
"""

    texto = analizar(
        data.image,
        prompt
    )

    return {
        "result": texto
    }

# =====================================================
# RECONOCER OBJETOS
# =====================================================

@app.post("/object")

def money(data: ImageRequest):

    prompt = """
Actúa como un asistente visual descriptivo para una persona ciega. Analiza la imagen actual y describe los objetos presentes siguiendo estrictamente estas reglas: 
1. Menciona primero el objeto principal o más cercano en el centro de la imagen. 
2. Indica su ubicación espacial relativa usando referencias claras (ej. "a tu izquierda", "al frente, a un paso de distancia", "sobre la mesa"). 
3. Describe de forma muy breve sus características físicas esenciales: color, tamaño aproximado, estado (si está abierto, cerrado, roto, encendido) y marcas o texto visible si es relevante para identificarlo.
4. Si hay objetos peligrosos o frágiles (como un vaso de vidrio al borde de la mesa, un cuchillo o cables sueltos), adviértelo de inmediato al inicio.
Sé sumamente conciso, directo y utiliza un tono descriptivo objetivo. Evita suposiciones o lenguaje florido.
"""

    texto = analizar(
        data.image,
        prompt
    )

    return {
        "result": texto
    }

# =====================================================
# CLIMA
# =====================================================

@app.post("/weather")

def money(data: ImageRequest):

    prompt = """
Actúa como un asistente meteorológico para una persona ciega. Analiza la fecha, hora, ubicación actual y la imagen del cielo o entorno que se te proporciona. Genera un reporte ultra-conciso que responda exactamente a lo siguiente:
1. Estado del cielo y temperatura actual (ej. "Cielo nublado, 18 grados").
2. Sensación térmica y previsión inmediata para las próximas horas (si hay probabilidad de lluvia, viento fuerte o calor extremo).
3. Recomendación directa y práctica para el usuario (ej. "Es necesario llevar paraguas", "Usa abrigo pesado", "Ponte gafas de sol y protector").
Sé directo, no uses introducciones ni saludos, y entrega la información en un máximo de tres frases cortas.
Menciona la fecha y la hora.
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
