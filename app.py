from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import phonenumbers
from phonenumbers import carrier, geocoder
from datetime import datetime
import sqlite3
import re
import os

app = FastAPI(title="Identificador Llamadas Colombia", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATOS COMPLETOS DE OPERADORES COLOMBIA ====================
OPERADORES_COLOMBIA = {
    # Claro
    "300": "Claro", "301": "Claro", "302": "Claro", "303": "Claro", "304": "Claro", "305": "Claro",
    "310": "Claro", "311": "Claro", "312": "Claro", "313": "Claro", "314": "Claro",
    "315": "Claro", "316": "Claro", "317": "Claro", "318": "Claro", "319": "Claro",
    # Movistar
    "320": "Movistar", "321": "Movistar", "322": "Movistar", "323": "Movistar", "324": "Movistar",
    # Tigo
    "325": "Tigo", "326": "Tigo", "327": "Tigo", "328": "Tigo", "329": "Tigo", "350": "Tigo",
    # WOM
    "351": "WOM", "352": "WOM", "353": "WOM", "354": "WOM",
    # Avantel
    "330": "Avantel", "331": "Avantel", "332": "Avantel",
    # Virgin Mobile
    "340": "Virgin Mobile", "341": "Virgin Mobile", "342": "Virgin Mobile",
    # ETB Móvil
    "355": "ETB Móvil", "356": "ETB Móvil",
    # Flash
    "360": "Flash", "361": "Flash", "362": "Flash",
    # Móvil Éxito
    "370": "Móvil Éxito", "371": "Móvil Éxito",
}

def identificar_operador_colombiano(numero):
    """Identifica el operador basado en el prefijo del número"""
    import re
    # Limpiar el número
    numero_limpio = re.sub(r'\D', '', numero)
    # Quitar código de país 57 si existe
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    # Verificar si es móvil colombiano (10 dígitos, empieza con 3)
    if len(numero_limpio) == 10 and numero_limpio.startswith("3"):
        prefijo = numero_limpio[:3]
        return OPERADORES_COLOMBIA.get(prefijo, None)
    return None

# ==================== MODELOS ====================
class PhoneRequest(BaseModel):
    phone: str

class SpamReport(BaseModel):
    phone: str
    category: str
    comment: Optional[str] = ""

# ==================== FUNCIONES DE BD ====================
def init_db():
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numeros_reportados (
            numero TEXT PRIMARY KEY,
            reportes INTEGER DEFAULT 1,
            ultimo_reporte TIMESTAMP,
            categoria TEXT DEFAULT 'spam',
            riesgo TEXT DEFAULT 'low'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def verificar_spam_bd(numero):
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    numero_limpio = re.sub(r'\D', '', numero)
    cursor.execute('SELECT reportes, riesgo FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return {'es_spam': True, 'reportes': resultado[0], 'riesgo': resultado[1]}
    return {'es_spam': False, 'reportes': 0}

def guardar_reporte(numero, categoria, comentario, ip):
    numero_limpio = re.sub(r'\D', '', numero)
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    cursor.execute('SELECT reportes FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
    existente = cursor.fetchone()
    if existente:
        nuevos_reportes = existente[0] + 1
        nuevo_riesgo = "high" if nuevos_reportes >= 10 else "medium" if nuevos_reportes >= 5 else "low"
        cursor.execute('''
            UPDATE numeros_reportados 
            SET reportes = ?, ultimo_reporte = ?, riesgo = ?, categoria = ?
            WHERE numero = ?
        ''', (nuevos_reportes, datetime.now().isoformat(), nuevo_riesgo, categoria, numero_limpio))
    else:
        cursor.execute('''
            INSERT INTO numeros_reportados (numero, reportes, ultimo_reporte, categoria, riesgo)
            VALUES (?, 1, ?, ?, 'low')
        ''', (numero_limpio, datetime.now().isoformat(), categoria))
    conn.commit()
    conn.close()
    return True

# ==================== ENDPOINTS ====================
@app.get("/")
def root():
    return {"message": "API Identificador Llamadas Colombia", "version": "3.0"}

@app.post("/identify")
async def identify_number(request: PhoneRequest):
    try:
        # Limpiar y parsear el número
        phone = request.phone
        parsed = phonenumbers.parse(phone, "CO")
        
        if not phonenumbers.is_valid_number(parsed):
            return {"valid": False, "error": "Número colombiano no válido"}
        
        # Identificar operador usando método local
        operador = identificar_operador_colombiano(phone)
        
        # Si no se encontró operador local, usar phonenumbers
        if not operador:
            operador = carrier.name_for_number(parsed, "es")
            if not operador:
                operador = "Desconocido"
        
        # Obtener ubicación
        ubicacion = geocoder.description_for_number(parsed, "es")
        if not ubicacion:
            ubicacion = "Colombia"
        
        # Determinar tipo
        if phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.MOBILE:
            tipo = "Móvil"
        elif phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.FIXED_LINE:
            tipo = "Fijo"
        else:
            tipo = "Otro"
        
        # Formatear
        nacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        internacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        # Verificar spam
        spam_info = verificar_spam_bd(phone)
        
        return {
            "valid": True,
            "national": nacional,
            "formatted": internacional,
            "type": tipo,
            "carrier": operador,
            "location": ubicacion,
            "spam_risk": spam_info['riesgo'] if spam_info['es_spam'] else "low",
            "reports": spam_info['reportes']
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

@app.post("/report")
async def report_spam(report: SpamReport, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    try:
        guardar_reporte(report.phone, report.category, report.comment, client_ip)
        return {"success": True, "message": "Reporte guardado"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
