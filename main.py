from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from transformers import pipeline

# Importamos las funciones de database.py
from database.database import init_db, insert_request, get_requests

app = FastAPI()
generator = pipeline("text-generation", model="gpt2")

@app.on_event("startup")
def startup_event():
    # Inicializa la base de datos (crea la tabla si no existe)
    init_db()

class GenerationRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 50
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0

@app.post("/generate")
def generate_text(req: GenerationRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío.")
    try:
        generated = generator(
            req.prompt,
            max_length=req.max_length,
            temperature=req.temperature,
            top_p=req.top_p,
            do_sample=True
        )
        text_result = generated[0]["generated_text"]

        # Guardar en BD
        insert_request(req.prompt, text_result)

        return {"generated_text": text_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando texto: {str(e)}")

@app.get("/history")
def get_history():
    rows = get_requests()
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "prompt": r[1],
            "generated_text": r[2],
            "created_at": r[3]
        })
    return {"history": results}


# RUTA BÁSICA (OPCIONAL) PARA PROBAR EL SERVIDOR
@app.get("/")
def read_root():
    return {"message": "API de generación de texto en funcionamiento"}

