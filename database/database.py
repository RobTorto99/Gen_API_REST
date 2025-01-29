import sqlite3
from datetime import datetime

# Inicializa la base de datos y crea la tabla si no existe
def init_db():
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            generated_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Inserta una nueva solicitud en la base de datos
def insert_request(prompt: str, generated_text: str):
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO requests (prompt, generated_text, created_at)
        VALUES (?, ?, ?)
    """, (prompt, generated_text, created_at))
    conn.commit()
    conn.close()

# Recupera todas las solicitudes del historial
def get_requests():
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, prompt, generated_text, created_at FROM requests")
    rows = cursor.fetchall()
    conn.close()
    return rows
