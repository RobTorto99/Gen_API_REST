# Gen_API_REST
Roams Back-end IA
Este proyecto implementa una API REST capaz de generar texto utilizando un modelo GPT-2 descargado de Hugging Face, además de almacenar un histórico de prompts en una base de datos SQLite.

1. Descripción
   -  Lenguaje: Python
   -  Framework: Flask
   -  Modelo IA: GPT-2 (descargado en tiempo de ejecución desde Hugging Face)
   -  Base de Datos (opcional): SQLite
   -  Documentación: Swagger UI (accesible en /api-docs)

El sistema:

   -  Recibe un prompt (texto) y genera una respuesta usando GPT-2.
   -  Permite ajustar parámetros: max_length, temperature, top_p.
   -  Guarda un histórico de prompts/respuestas en una tabla de SQLite.
   -  Provee una interfaz HTML básica y un endpoint JSON para integrar fácilmente con clientes externos.
   -  Ofrece un endpoint /history para recuperar el histórico de todas las solicitudes.

2. Requisitos y Dependencias
Asegúrate de tener Python 3.7+ instalado. Dentro de la carpeta del proyecto:

- Crear un entorno virtual:

python3 -m venv venv

En Linux/Mac
source venv/bin/activate

En Windows:
venv\Scripts\activate

- Instalar las dependencias:

pip install -r requirements.txt

3. Cómo Ejecutar la API
- Activar entorno virtual:
source venv/bin/activate

- Iniciar la aplicación Flask:
python main.py

Si todo carga correctamente, verás mensajes en la consola indicando que Flask corre en:
Running on http://127.0.0.1:5000

- Abre en tu navegador http://127.0.0.1:5000 para la interfaz HTML de prueba.
- Visita http://127.0.0.1:5000/api-docs para ver la documentación Swagger interactiva.
- Para cerrarla utilizar Ctrl + C en la terminal.

4. Ejemplos de Solicitudes
- Interfaz HTML
- Navega a http://127.0.0.1:5000.
- Ingresa un prompt y ajusta parámetros (max_length, temperature, top_p).
- Pulsa Generar para ver la respuesta generada.

5. Desarrollo Interno
- Descarga dinámica del modelo GPT-2:
Al correr python main.py por primera vez, si el modelo GPT-2 no está en caché, se descargará automáticamente desde Hugging Face (AutoModelForCausalLM.from_pretrained("gpt2")).
- Persistencia:
Se usa SQLite para almacenar cada prompt y respuesta generada.
La creación de la tabla se hace al iniciar la app en init_db().
- Logs:
Se configuran logs en app.log, que registra cada request y response, y mensajes de error.
