import logging
from flask import Flask, request, jsonify, render_template_string
from flask_swagger_ui import get_swaggerui_blueprint
from database.database import init_db, insert_request, get_requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)

# ------------------------------
# 1. CONFIGURACIÓN DE LOGGING
# ------------------------------
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------
# 2. CARGA DEL MODELO GPT-2
# ------------------------------
model_name = "gpt2"

def load_model():
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    return tokenizer, model

tokenizer, model = load_model()

def generate_response(prompt, max_length, temperature, top_p):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    output = model.generate(
        **inputs,
        max_length=max_length,
        temperature=temperature,
        top_p=top_p,
        do_sample=True,
        repetition_penalty=1.2
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)

with app.app_context():
    init_db()

# ------------------------------
# 3. HOOKS DE LOG (REQUEST/RESPONSE)
# ------------------------------
@app.before_request
def log_request_info():
    logger.info(f"Request {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response {response.status_code} for {request.path}")
    return response

# ------------------------------
# 4. DOCUMENTACIÓN SWAGGER UI 
# ------------------------------
SWAGGER_URL = '/api-docs'
API_DEFINITION = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_DEFINITION)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ------------------------------
# 5. PLANTILLA HTML
# ------------------------------
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat con GPT-2</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        h1 {
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        textarea {
            width: 100%;
            height: 80px;
            font-size: 1em;
            padding: 8px;
        }
        .output {
            margin-top: 20px;
            white-space: pre-wrap;
            background-color: #f9f9f9;
            border-left: 4px solid #007BFF;
            padding: 10px;
        }
        .label {
            font-weight: bold;
        }
        .submit-btn {
            padding: 10px;
            font-size: 1em;
            background-color: #007BFF;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .submit-btn:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chat con GPT-2</h1>
        <form method="POST">
            <label for="prompt" class="label">Ingresa tu pregunta o prompt:</label>
            <textarea name="prompt" id="prompt" required>{{ prompt_text if prompt_text else "" }}</textarea>
            <label for="max_length" class="label">Longitud máxima:</label>
            <input type="number" name="max_length" id="max_length" value="{{ max_length if max_length else 50 }}"/>
            <label for="temperature" class="label">Temperatura:</label>
            <input type="number" step="0.1" name="temperature" id="temperature" value="{{ temperature if temperature else 0.7 }}"/>
            <label for="top_p" class="label">Top-p:</label>
            <input type="number" step="0.1" name="top_p" id="top_p" value="{{ top_p if top_p else 0.9 }}"/>
            <button type="submit" class="submit-btn">Generar</button>
        </form>

        {% if generated_text %}
            <div class="output">
                <div><strong>Prompt:</strong> {{ prompt_text }}</div>
                <div><strong>Respuesta:</strong> {{ generated_text }}</div>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# ------------------------------
# 6. ENDPOINT PRINCIPAL 
# ------------------------------
@app.route("/", methods=["GET", "POST"])
def root_endpoint():
    wants_json = "application/json" in request.headers.get("Accept", "")

    if request.method == "GET":
        if wants_json:
            return jsonify({"message": "Usa POST / para enviar prompt en JSON"}), 200
        else:
            return render_template_string(html_page)

    # POST
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "El prompt no puede estar vacío"}), 400

    max_length = data.get("max_length", 50)
    temperature = data.get("temperature", 0.7)
    top_p = data.get("top_p", 0.9)

    try:
        generated_text = generate_response(
            prompt,
            int(max_length),
            float(temperature),
            float(top_p)
        )
        insert_request(prompt, generated_text)

        return jsonify({"generated_text": generated_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------
# 7. ENDPOINT PÚBLICO: /history 
# ------------------------------
@app.route("/history", methods=["GET"])
def get_history():
    try:
        rows = get_requests()
        results = [
            {
                "id": row[0],
                "prompt": row[1],
                "generated_text": row[2],
                "created_at": row[3]
            }
            for row in rows
        ]
        return jsonify({"history": results}), 200
    except Exception as e:
        return jsonify({"error": f"Error obteniendo el historial: {str(e)}"}), 500

# ------------------------------
# 8. INICIO DE LA APLICACIÓN
# ------------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
