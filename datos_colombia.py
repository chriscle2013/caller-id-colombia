# datos_colombia.py - Base de datos de operadores y ciudades de Colombia
import phonenumbers
from phonenumbers import carrier, geocoder

# Diccionario de prefijos de operadores móviles en Colombia
OPERADORES_COLOMBIA = {
    # Claro
    "300": "Claro", "301": "Claro", "302": "Claro", "303": "Claro", 
    "304": "Claro", "305": "Claro", "310": "Claro", "311": "Claro",
    "312": "Claro", "313": "Claro", "314": "Claro",
    
    # Movistar
    "315": "Movistar", "316": "Movistar", "317": "Movistar", 
    "318": "Movistar", "319": "Movistar",
    
    # Tigo
    "320": "Tigo", "321": "Tigo", "322": "Tigo", 
    "323": "Tigo", "324": "Tigo",
    
    # WOM
    "350": "WOM", "351": "WOM",
    
    # Avantel
    "330": "Avantel", "331": "Avantel",
    
    # Virgin Mobile
    "340": "Virgin Mobile", "341": "Virgin Mobile",
    
    # ETB (fijo)
    "601": "ETB", "571": "ETB",
}

# Diccionario de códigos de ciudad (fijos)
CIUDADES_COLOMBIA = {
    "1": "Bogotá",
    "2": "Cali",
    "4": "Medellín",
    "5": "Barranquilla",
    "6": "Pereira",
    "7": "Bucaramanga",
    "8": "Cartagena",
}

def identificar_operador_colombiano(numero):
    """Identifica el operador basado en el prefijo colombiano"""
    # Limpiar el número (quitar +57, espacios, etc.)
    numero_limpio = ''.join(filter(str.isdigit, numero))
    
    # Quitar código de país si existe (+57 o 57)
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    # Para móviles (10 dígitos, empieza con 3)
    if len(numero_limpio) == 10 and numero_limpio.startswith("3"):
        prefijo = numero_limpio[:3]
        return OPERADORES_COLOMBIA.get(prefijo, "Operador desconocido")
    
    # Para fijos (7 u 8 dígitos, empieza con 6, 7, 8, etc.)
    elif len(numero_limpio) in [7, 8] and numero_limpio.startswith(("6", "7", "8")):
        return "Línea fija"
    
    return "Operador no identificado"

def identificar_ciudad_colombiana(numero):
    """Identifica la ciudad basada en el prefijo para números fijos"""
    numero_limpio = ''.join(filter(str.isdigit, numero))
    
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    # Para números fijos, el primer dígito indica la ciudad
    if len(numero_limpio) in [7, 8] and numero_limpio.startswith(("6", "7", "8")):
        primer_digito = numero_limpio[0]
        return CIUDADES_COLOMBIA.get(primer_digito, "Colombia")
    
    return "Colombia"

def obtener_info_completa(phone_number):
    """Obtiene información completa del número (combina phonenumbers + datos locales)"""
    try:
        parsed = phonenumbers.parse(phone_number, "CO")
        
        if not phonenumbers.is_valid_number(parsed):
            return None
        
        # Obtener info de phonenumbers
        carrier_name = carrier.name_for_number(parsed, "es")
        location = geocoder.description_for_number(parsed, "es")
        
        # Mejorar con datos locales
        operador_local = identificar_operador_colombiano(phone_number)
        ciudad_local = identificar_ciudad_colombiana(phone_number)
        
        # Usar datos locales si phonenumbers no tiene información
        if not carrier_name or carrier_name == "Desconocido":
            carrier_name = operador_local
        
        if not location or location == "Colombia":
            location = ciudad_local
        
        # Determinar tipo de número
        number_type = phonenumbers.number_type(parsed)
        if number_type == phonenumbers.PhoneNumberType.MOBILE:
            tipo = "Móvil"
        elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
            tipo = "Fijo"
        else:
            tipo = "Otro"
        
        return {
            'valid': True,
            'type': tipo,
            'carrier': carrier_name,
            'location': location,
            'operador_detallado': operador_local,
            'ciudad_detectada': ciudad_local
        }
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}

# Prueba rápida
if __name__ == "__main__":
    numeros_prueba = [
        "+573001234567",  # Claro Bogotá
        "+573152345678",  # Movistar
        "+573202345678",  # Tigo
        "+573502345678",  # WOM
        "6012345678",     # Fijo Bogotá
        "412345678",      # Fijo Medellín
    ]
    
    print("=" * 60)
    print("📊 PRUEBA DE DATOS COLOMBIANOS")
    print("=" * 60)
    
    for numero in numeros_prueba:
        info = obtener_info_completa(numero)
        if info and info['valid']:
            print(f"\n📞 {numero}")
            print(f"   Tipo: {info['type']}")
            print(f"   Operador: {info['carrier']}")
            print(f"   Ubicación: {info['location']}")
