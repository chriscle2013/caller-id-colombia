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

app = FastAPI(title="Identificador Llamadas Colombia", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CÓDIGOS DE RED (MNC) ACTUALIZADOS ====================
# Estos son los identificadores de operador que devuelve phonenumbers
MNC_OPERADORES = {
    # Claro
    "101": "Claro",
    "154": "Claro", 
    "199": "Claro",
    
    # Movistar
    "001": "Movistar",
    "102": "Movistar",
    "123": "Movistar",
    "154": "Movistar",
    "199": "Movistar",
    
    # Tigo
    "020": "Tigo",
    "103": "Tigo",
    "111": "Tigo",
    "165": "Tigo",
    "187": "Tigo",
    "208": "Tigo",
    
    # WOM
    "351": "WOM",
    "352": "WOM",
    "353": "WOM",
    "354": "WOM",
    
    # Avantel
    "130": "Avantel",
    
    # ETB
    "187": "ETB",
    
    # Virgin Mobile (usa red de Avantel)
    "340": "Virgin Mobile",
    "341": "Virgin Mobile",
    "342": "Virgin Mobile",
}

# ==================== PREFIJOS (RESPALDO - menos confiable) ====================
PREFIJOS_RESPALDO = {
    "300": "Claro", "301": "Claro", "302": "Claro", "303": "Claro", "304": "Claro", "305": "Claro",
    "310": "Claro", "311": "Claro", "312": "Claro", "313": "Claro", "314": "Claro",
    "315": "Claro", "316": "Claro", "317": "Claro", "318": "Claro", "319": "Claro",
    "320": "Movistar", "321": "Movistar", "322": "Movistar", "323": "Movistar", "324": "Movistar",
    "325": "Tigo", "326": "Tigo", "327": "Tigo", "328": "Tigo", "329": "Tigo", "350": "Tigo",
    "351": "WOM", "352": "WOM", "353": "WOM", "354": "WOM",
    "330": "Avantel", "331": "Avantel", "332": "Avantel",
    "340": "Virgin Mobile", "341": "Virgin Mobile", "342": "Virgin Mobile",
    "355": "ETB Móvil", "356": "ETB Móvil",
}

# ==================== CIUDADES ====================
CIUDADES = {
    "1": "Bogotá", "2": "Cali", "4": "Medellín", "5": "Barranquilla",
    "6": "Pereira", "7": "Bucaramanga", "8": "Cartagena",
}

# ==================== EMERGENCIAS ====================
EMERGENCIAS = {
    "112": "Emergencia general (Policía/Bomberos/SAMU)",
    "123": "Policía Nacional",
    "125": "SAMU - Emergencias médicas",
    "132": "Bomberos",
}

# ==================== MODELOS ====================
class PhoneRequest(BaseModel):
    phone: str

class SpamReport(BaseModel):
    phone: str
    category: str
    comment: Optional[str] = ""

# ==================== BD ====================
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

def limpiar_numero(numero: str) -> str:
    solo_digitos = re.sub(r'\D', '', numero)
    if solo_digitos.startswith('57'):
        solo_digitos = solo_digitos[2:]
    return solo_digitos

def verificar_spam_bd(numero: str):
    numero_limpio = limpiar_numero(numero)
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    cursor.execute('SELECT reportes, riesgo, categoria FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return {'es_spam': True, 'reportes': resultado[0], 'riesgo': resultado[1], 'categoria': resultado[2]}
    return {'es_spam': False, 'reportes': 0, 'riesgo': 'low'}

def guardar_reporte(numero: str, categoria: str, comentario: str, ip: str):
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

# ==================== FUNCIONES DE IDENTIFICACIÓN ====================
def identificar_operador_por_mnc(numero: str, parsed) -> str:
    """Identifica operador usando el código de red (MNC) - método más confiable"""
    try:
        # Obtener el código de red (MNC) usando la biblioteca phonenumbers
        # El código de red viene en el formato "Colombia xxx"
        nombre_operador = carrier.name_for_number(parsed, "es")
        
        # Si phonenumbers devuelve un nombre, intentamos mapearlo
        if nombre_operador:
            # Limpiar el nombre
            nombre_operador = nombre_operador.strip()
            
            # Mapeo de nombres a operadores estandarizados
            if "CLARO" in nombre_operador.upper():
                return "Claro"
            elif "MOVISTAR" in nombre_operador.upper():
                return "Movistar"
            elif "TIGO" in nombre_operador.upper():
                return "Tigo"
            elif "WOM" in nombre_operador.upper():
                return "WOM"
            elif "AVANTEL" in nombre_operador.upper():
                return "Avantel"
            elif "VIRGIN" in nombre_operador.upper():
                return "Virgin Mobile"
            elif "ETB" in nombre_operador.upper():
                return "ETB Móvil"
        
        return None
    except:
        return None

def identificar_operador_por_prefijo(numero: str) -> str:
    """Identifica operador por prefijo - método de respaldo"""
    numero_limpio = limpiar_numero(numero)
    if len(numero_limpio) == 10 and numero_limpio.startswith("3"):
        prefijo = numero_limpio[:3]
        return PREFIJOS_RESPALDO.get(prefijo)
    return None

def identificar_ciudad(numero: str) -> str:
    """Identifica ciudad para números fijos"""
    numero_limpio = limpiar_numero(numero)
    if len(numero_limpio) in [7, 8] and numero_limpio.startswith(("6", "7", "8")):
        primer_digito = numero_limpio[0]
        return CIUDADES.get(primer_digito, "Colombia")
    return "Colombia"

def verificar_emergencia(numero: str):
    numero_limpio = limpiar_numero(numero)
    return EMERGENCIAS.get(numero_limpio)

# ==================== ENDPOINTS ====================
@app.get("/")
def root():
    return {"message": "API Identificador Llamadas Colombia", "version": "4.0", "status": "online"}

@app.post("/identify")
async def identify_number(request: PhoneRequest):
    try:
        # Verificar emergencia
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
        
        # IDENTIFICAR OPERADOR - Método 1: Código de red (más confiable)
        operador = identificar_operador_por_mnc(request.phone, parsed)
        
        # Método 2: Prefijo (respaldo)
        if not operador:
            operador = identificar_operador_por_prefijo(request.phone)
        
        # Método 3: phonenumbers como último respaldo
        if not operador:
            operador = carrier.name_for_number(parsed, "es")
            if not operador:
                operador = "Desconocido"
        
        # Limpiar el nombre del operador si es muy largo
        if len(operador) > 20:
            operador = operador.split()[0] if ' ' in operador else operador[:15]
        
        # Determinar tipo de número
        number_type = phonenumbers.number_type(parsed)
        if number_type == phonenumbers.PhoneNumberType.MOBILE:
            tipo = "Móvil"
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            tipo = "Fijo"
        else:
            tipo = "Otro"
        
        # Formatear número
        formato_internacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        formato_nacional = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        # Identificar ciudad
        ubicacion = identificar_ciudad(request.phone)
        
        # Verificar spam en BD
        spam_info = verificar_spam_bd(request.phone)
        
        return {
            "valid": True,
            "formatted": formato_internacional,
            "national": formato_nacional,
            "type": tipo,
            "carrier": operador,
            "location": ubicacion,
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
        return {"success": True, "message": "Gracias por reportar. Ayudas a la comunidad colombiana."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/check-spam/{phone}")
async def check_spam(phone: str):
    resultado = verificar_spam_bd(phone)
    return resultado

@app.get("/emergencias")
async def get_emergencias():
    return EMERGENCIAS

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
