# app.py - Versión completa con datos mejorados de Colombia
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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

# ==================== DATOS COMPLETOS COLOMBIA ====================
OPERADORES_COLOMBIA_COMPLETO = {
    "300": "Claro", "301": "Claro", "302": "Claro", "303": "Claro", "304": "Claro",
    "305": "Claro", "310": "Claro", "311": "Claro", "312": "Claro", "313": "Claro",
    "314": "Claro", "315": "Claro", "316": "Claro", "317": "Claro", "318": "Claro",
    "319": "Claro", "320": "Movistar", "321": "Movistar", "322": "Movistar",
    "323": "Movistar", "324": "Movistar", "325": "Tigo", "326": "Tigo",
    "327": "Tigo", "328": "Tigo", "329": "Tigo", "350": "Tigo", "351": "WOM",
    "352": "WOM", "353": "WOM", "354": "WOM", "330": "Avantel", "331": "Avantel",
    "332": "Avantel", "340": "Virgin Mobile", "341": "Virgin Mobile", "342": "Virgin Mobile",
    "355": "ETB Móvil", "356": "ETB Móvil", "360": "Flash", "361": "Flash",
    "362": "Flash", "370": "Móvil Éxito", "371": "Móvil Éxito",
}

CIUDADES_COLOMBIA_COMPLETO = {
    "1": {"ciudad": "Bogotá", "departamento": "Cundinamarca"},
    "2": {"ciudad": "Cali", "departamento": "Valle del Cauca"},
    "4": {"ciudad": "Medellín", "departamento": "Antioquia"},
    "5": {"ciudad": "Barranquilla", "departamento": "Atlántico"},
    "6": {"ciudad": "Pereira", "departamento": "Risaralda"},
    "7": {"ciudad": "Bucaramanga", "departamento": "Santander"},
    "8": {"ciudad": "Cartagena", "departamento": "Bolívar"},
    "9": {"ciudad": "Cúcuta", "departamento": "Norte de Santander"},
}

EMERGENCIAS_COLOMBIA = {
    "112": "Emergencia general (Policía/Bomberos/SAMU)",
    "123": "Policía Nacional",
    "125": "SAMU - Emergencias médicas",
    "132": "Bomberos",
    "144": "Línea amiga - Prevención suicidio",
    "147": "Fiscalía - Denuncias",
    "155": "ICBF - Bienestar familiar",
    "159": "Tránsito - Movilidad",
    "165": "Defensa Civil",
    "192": "Cruz Roja",
}

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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            categoria TEXT,
            comentario TEXT,
            ip TEXT,
            fecha TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def limpiar_numero(numero):
    solo_digitos = re.sub(r'\D', '', numero)
    if solo_digitos.startswith('57'):
        solo_digitos = solo_digitos[2:]
    return solo_digitos

def verificar_spam_bd(numero):
    numero_limpio = limpiar_numero(numero)
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    cursor.execute('SELECT reportes, riesgo, categoria FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {'es_spam': True, 'reportes': resultado[0], 'riesgo': resultado[1], 'categoria': resultado[2]}
    return {'es_spam': False, 'reportes': 0}

def guardar_reporte(numero, categoria, comentario, ip):
    numero_limpio = limpiar_numero(numero)
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT reportes, riesgo FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
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
    
    cursor.execute('''
        INSERT INTO reportes (numero, categoria, comentario, ip, fecha)
        VALUES (?, ?, ?, ?, ?)
    ''', (numero_limpio, categoria, comentario, ip, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

# ==================== FUNCIONES MEJORADAS ====================
def identificar_operador_detallado(numero):
    numero_limpio = re.sub(r'\D', '', numero)
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    if len(numero_limpio) == 10 and numero_limpio.startswith("3"):
        prefijo = numero_limpio[:3]
        return OPERADORES_COLOMBIA_COMPLETO.get(prefijo)
    return None

def identificar_ciudad_departamento(numero):
    numero_limpio = re.sub(r'\D', '', numero)
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    if len(numero_limpio) in [7, 8] and numero_limpio[0] in CIUDADES_COLOMBIA_COMPLETO:
        ciudad_info = CIUDADES_COLOMBIA_COMPLETO[numero_limpio[0]]
        return f"{ciudad_info['ciudad']}, {ciudad_info['departamento']}"
    return None

def verificar_emergencia(numero):
    numero_limpio = re.sub(r'\D', '', numero)
    return EMERGENCIAS_COLOMBIA.get(numero_limpio)

# ==================== ENDPOINTS ====================
@app.get("/")
async def root():
    return {
        "message": "API Identificador Llamadas Colombia",
        "version": "3.0",
        "status": "online",
        "features": ["identify", "report_spam", "check_spam"],
        "colombia_data": {
            "operadores": len(OPERADORES_COLOMBIA_COMPLETO),
            "ciudades": len(CIUDADES_COLOMBIA_COMPLETO),
            "emergencias": len(EMERGENCIAS_COLOMBIA)
        }
    }

@app.post("/identify")
async def identify_number(request: PhoneRequest):
    try:
        # Verificar emergencias primero
        emergencia = verificar_emergencia(request.phone)
        if emergencia:
            return {
                "valid": True,
                "type": "Emergencia",
                "carrier": "Servicio de emergencia",
                "location": "Colombia",
                "national": request.phone,
                "formatted": request.phone,
                "is_emergency": True,
                "emergency_info": emergencia,
                "spam_risk": "low",
                "reports": 0
            }
        
        parsed = phonenumbers.parse(request.phone, "CO")
        
        if not phonenumbers.is_valid_number(parsed):
            return {"valid": False, "error": "Número colombiano no válido"}
        
        # Información básica
        carrier_name = carrier.name_for_number(parsed, "es")
        location = geocoder.description_for_number(parsed, "es")
        
        # Mejorar con datos locales
        operador_local = identificar_operador_detallado(request.phone)
        ciudad_local = identificar_ciudad_departamento(request.phone)
        
        carrier_name = operador_local if operador_local else (carrier_name or "Desconocido")
        location = ciudad_local if ciudad_local else (location or "Colombia")
        
        # Tipo de número
        number_type = phonenumbers.number_type(parsed)
        if number_type == phonenumbers.PhoneNumberType.MOBILE:
            tipo = "Móvil"
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            tipo = "Fijo"
        else:
            tipo = "Otro"
        
        # Verificar spam en BD
        spam_info = verificar_spam_bd(request.phone)
        
        # Formatear
        formato_internacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        formato_nacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        return {
            "valid": True,
            "formatted": formato_internacional,
            "national": formato_nacional,
            "type": tipo,
            "carrier": carrier_name,
            "location": location,
            "spam_risk": spam_info['riesgo'] if spam_info['es_spam'] else "low",
            "reports": spam_info['reportes'],
            "is_reported": spam_info['es_spam'],
            "is_emergency": False
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

@app.post("/report")
async def report_spam(report: SpamReport, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        guardar_reporte(report.phone, report.category, report.comment, client_ip)
        return {
            "success": True,
            "message": "Gracias por reportar. Ayudas a la comunidad colombiana."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/check-spam/{phone}")
async def check_spam(phone: str):
    resultado = verificar_spam_bd(phone)
    return resultado

@app.get("/emergencias")
async def get_emergencias():
    """Lista todos los números de emergencia en Colombia"""
    return EMERGENCIAS_COLOMBIA

@app.get("/estadisticas")
async def get_estadisticas():
    """Estadísticas de operadores en Colombia"""
    stats = {}
    for prefijo, operador in OPERADORES_COLOMBIA_COMPLETO.items():
        if operador not in stats:
            stats[operador] = 0
        stats[operador] += 1
    return stats

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)