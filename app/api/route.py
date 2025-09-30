from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
from huggingface_hub import InferenceClient

# Configuración
logger = logging.getLogger(__name__)
app = FastAPI()

# Configurar HF token desde variables de entorno
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/Phi-4-mini-flash-reasoning")

# Cliente de Hugging Face
client = InferenceClient(token=HF_TOKEN)

class Query(BaseModel):
    question: str
    session_id: str = "default"

class Feedback(BaseModel):
    question: str
    response: str
    correct_response: str

def build_prompt(question: str) -> str:
    """Construye el prompt para el modelo - Adaptado de tu model.py"""
    return f"""
[INST] <<SYS>>
Eres Daniel Rada, experto en infraestructura cloud y ciberseguridad con 10+ años de experiencia.
Responde de forma concisa y profesional en el mismo idioma de la pregunta.
Si no sabes algo, di "No tengo información sobre eso en mi experiencia".
<</SYS>>

Pregunta: {question}
[/INST]
"""

@app.post("/ask")
async def ask_question(query: Query):
    try:
        logger.info(f"Pregunta recibida: {query.question}")
        
        # Construir prompt
        prompt = build_prompt(query.question)
        
        # Llamar a Hugging Face API
        response = client.text_generation(
            prompt,
            model=MODEL_NAME,
            max_new_tokens=512,
            temperature=0.3,
            do_sample=True,
            return_full_text=False
        )
        
        logger.info(f"Respuesta generada: {response[:200]}...")
        return {"answer": response}
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"answer": "Lo siento, ocurrió un error al procesar tu pregunta"}

@app.post("/feedback")
async def receive_feedback(feedback: Feedback):
    try:
        # En un entorno real, guardarías en una base de datos
        logger.info(f"Feedback recibido: {feedback.question}")
        return {"status": "feedback received"}
    except Exception as e:
        return {"status": "error"}

@app.get("/")
async def health_check():
    return {"status": "OK", "model": MODEL_NAME}

# Handler para Vercel
async def handler(request):
    return await app(request)
