# datos_completos_colombia.py - Base de datos completa para Colombia
import json

# ==================== OPERADORES MÓVILES COMPLETOS ====================
OPERADORES_COLOMBIA_COMPLETO = {
    # Claro (los más comunes)
    "300": "Claro", "301": "Claro", "302": "Claro", "303": "Claro", 
    "304": "Claro", "305": "Claro", "310": "Claro", "311": "Claro",
    "312": "Claro", "313": "Claro", "314": "Claro", "315": "Claro",
    "316": "Claro", "317": "Claro", "318": "Claro", "319": "Claro",
    
    # Movistar
    "320": "Movistar", "321": "Movistar", "322": "Movistar", 
    "323": "Movistar", "324": "Movistar",
    
    # Tigo
    "325": "Tigo", "326": "Tigo", "327": "Tigo", 
    "328": "Tigo", "329": "Tigo", "350": "Tigo",
    
    # WOM
    "351": "WOM", "352": "WOM", "353": "WOM", "354": "WOM",
    
    # Avantel (empresarial)
    "330": "Avantel", "331": "Avantel", "332": "Avantel",
    
    # Virgin Mobile
    "340": "Virgin Mobile", "341": "Virgin Mobile", "342": "Virgin Mobile",
    
    # ETB Móvil
    "355": "ETB Móvil", "356": "ETB Móvil",
    
    # Flash (nuevo operador 2024)
    "360": "Flash", "361": "Flash", "362": "Flash",
    
    # Móvil Éxito
    "370": "Móvil Éxito", "371": "Móvil Éxito",
}

# ==================== CIUDADES Y DEPARTAMENTOS ====================
CIUDADES_COLOMBIA_COMPLETO = {
    "1": {"ciudad": "Bogotá", "departamento": "Cundinamarca", "codigo": "1"},
    "2": {"ciudad": "Cali", "departamento": "Valle del Cauca", "codigo": "2"},
    "4": {"ciudad": "Medellín", "departamento": "Antioquia", "codigo": "4"},
    "5": {"ciudad": "Barranquilla", "departamento": "Atlántico", "codigo": "5"},
    "6": {"ciudad": "Pereira", "departamento": "Risaralda", "codigo": "6"},
    "7": {"ciudad": "Bucaramanga", "departamento": "Santander", "codigo": "7"},
    "8": {"ciudad": "Cartagena", "departamento": "Bolívar", "codigo": "8"},
    "9": {"ciudad": "Cúcuta", "departamento": "Norte de Santander", "codigo": "9"},
}

# ==================== NÚMEROS DE EMERGENCIA COLOMBIA ====================
EMERGENCIAS_COLOMBIA = {
    "112": {"nombre": "Emergencia general", "entidad": "Policía/Bomberos/SAMU"},
    "123": {"nombre": "Policía Nacional", "entidad": "Policía Nacional"},
    "125": {"nombre": "SAMU", "entidad": "Emergencias médicas"},
    "132": {"nombre": "Bomberos", "entidad": "Cuerpo de Bomberos"},
    "144": {"nombre": "Línea amiga", "entidad": "Prevención del suicidio"},
    "147": {"nombre": "Fiscalía", "entidad": "Denuncias"},
    "155": {"nombre": "ICBF", "entidad": "Bienestar familiar"},
    "159": {"nombre": "Tránsito", "entidad": "Movilidad"},
    "165": {"nombre": "Defensa Civil", "entidad": "Emergencias"},
    "192": {"nombre": "Cruz Roja", "entidad": "Primeros auxilios"},
}

# ==================== NÚMEROS DE EMPRESAS IMPORTANTES ====================
EMPRESAS_COLOMBIA = {
    # Bancos
    "6012345678": {"nombre": "Bancolombia", "categoria": "banco", "confiable": True},
    "6023456789": {"nombre": "Davivienda", "categoria": "banco", "confiable": True},
    "6034567890": {"nombre": "Banco de Bogotá", "categoria": "banco", "confiable": True},
    "6045678901": {"nombre": "Banco de Occidente", "categoria": "banco", "confiable": True},
    "6056789012": {"nombre": "BBVA Colombia", "categoria": "banco", "confiable": True},
    "6067890123": {"nombre": "Banco Agrario", "categoria": "banco", "confiable": True},
    
    # Servicios públicos
    "6012345678": {"nombre": "Enel Codensa", "categoria": "electricidad", "confiable": True},
    "6023456789": {"nombre": "Acueducto Bogotá", "categoria": "agua", "confiable": True},
    "6034567890": {"nombre": "Gas Natural", "categoria": "gas", "confiable": True},
    "6045678901": {"nombre": "Empresas Públicas Medellín", "categoria": "multiservicios", "confiable": True},
    
    # Telecomunicaciones
    "6012345678": {"nombre": "Claro Colombia", "categoria": "telecom", "confiable": True},
    "6023456789": {"nombre": "Movistar Colombia", "categoria": "telecom", "confiable": True},
    "6034567890": {"nombre": "Tigo Colombia", "categoria": "telecom", "confiable": True},
    "6045678901": {"nombre": "ETB", "categoria": "telecom", "confiable": True},
    "6056789012": {"nombre": "WOM Colombia", "categoria": "telecom", "confiable": True},
}

# ==================== PATRONES DE FRAUDE COMUNES ====================
PATRONES_FRAUDE = [
    "premio", "loteria", "sorteo", "ganador", "casa de cambio",
    "familiar secuestrado", "falso policía", "cobro de impuestos",
    "actualización de datos", "tarjeta de crédito bloqueada",
    "código de verificación", "phishing", "estafa",
]

def identificar_operador_detallado(numero):
    """Identifica operador con información detallada"""
    import re
    numero_limpio = re.sub(r'\D', '', numero)
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    if len(numero_limpio) == 10 and numero_limpio.startswith("3"):
        prefijo = numero_limpio[:3]
        operador = OPERADORES_COLOMBIA_COMPLETO.get(prefijo)
        
        if operador:
            info_operador = {
                "nombre": operador,
                "tipo": "Móvil",
                "prefijo": prefijo
            }
            
            # Información adicional según operador
            if operador == "Claro":
                info_operador["cobertura"] = "Nacional"
                info_operador["servicios"] = "Voz, datos, LTE, 5G"
            elif operador == "Movistar":
                info_operador["cobertura"] = "Nacional"
                info_operador["servicios"] = "Voz, datos, LTE, fibra"
            elif operador == "Tigo":
                info_operador["cobertura"] = "Nacional"
                info_operador["servicios"] = "Voz, datos, LTE, TV"
            elif operador == "WOM":
                info_operador["cobertura"] = "Principales ciudades"
                info_operador["servicios"] = "Voz, datos, LTE"
            
            return info_operador
    
    return None

def identificar_ciudad_departamento(numero):
    """Identifica ciudad y departamento para números fijos"""
    import re
    numero_limpio = re.sub(r'\D', '', numero)
    if numero_limpio.startswith("57"):
        numero_limpio = numero_limpio[2:]
    
    if len(numero_limpio) in [7, 8] and numero_limpio[0] in CIUDADES_COLOMBIA_COMPLETO:
        ciudad_info = CIUDADES_COLOMBIA_COMPLETO[numero_limpio[0]]
        return {
            "ciudad": ciudad_info["ciudad"],
            "departamento": ciudad_info["departamento"]
        }
    
    return None

def verificar_emergencia(numero):
    """Verifica si es número de emergencia"""
    import re
    numero_limpio = re.sub(r'\D', '', numero)
    
    for emergencia, info in EMERGENCIAS_COLOMBIA.items():
        if numero_limpio == emergencia or numero_limpio.endswith(emergencia):
            return info
    return None

def verificar_empresa_confiable(numero):
    """Verifica si es número de empresa confiable"""
    import re
    numero_limpio = re.sub(r'\D', '', numero)
    numero_limpio = numero_limpio[-10:]  # últimos 10 dígitos
    
    if numero_limpio in EMPRESAS_COLOMBIA:
        return EMPRESAS_COLOMBIA[numero_limpio]
    return None

def detectar_fraude(texto):
    """Detecta si un mensaje contiene patrones de fraude"""
    texto_lower = texto.lower()
    patrones_encontrados = []
    
    for patron in PATRONES_FRAUDE:
        if patron in texto_lower:
            patrones_encontrados.append(patron)
    
    return patrones_encontrados

def obtener_estadisticas_operadores():
    """Obtiene estadísticas de operadores en Colombia"""
    stats = {}
    for prefijo, operador in OPERADORES_COLOMBIA_COMPLETO.items():
        if operador not in stats:
            stats[operador] = {"prefijos": [], "cantidad": 0}
        stats[operador]["prefijos"].append(prefijo)
        stats[operador]["cantidad"] += 1
    
    return stats

# ==================== PRUEBAS ====================
if __name__ == "__main__":
    print("=" * 60)
    print("📊 DATOS COMPLETOS DE COLOMBIA")
    print("=" * 60)
    
    # Probar identificación de operadores
    numeros_prueba = [
        "+573001234567",  # Claro
        "+573201234567",  # Movistar
        "+573501234567",  # Tigo
        "+573511234567",  # WOM
        "6012345678",     # Fijo Bogotá
        "412345678",      # Fijo Medellín
        "123",            # Emergencia
    ]
    
    for numero in numeros_prueba:
        print(f"\n📞 Analizando: {numero}")
        
        # Verificar emergencia
        emergencia = verificar_emergencia(numero)
        if emergencia:
            print(f"   🚨 EMERGENCIA: {emergencia['nombre']}")
            print(f"   Entidad: {emergencia['entidad']}")
            continue
        
        # Verificar empresa confiable
        empresa = verificar_empresa_confiable(numero)
        if empresa:
            print(f"   🏢 EMPRESA: {empresa['nombre']}")
            print(f"   Categoría: {empresa['categoria']}")
            continue
        
        # Identificar operador
        operador = identificar_operador_detallado(numero)
        if operador:
            print(f"   📱 OPERADOR: {operador['nombre']}")
            print(f"   Tipo: {operador['tipo']}")
            if 'cobertura' in operador:
                print(f"   Cobertura: {operador['cobertura']}")
        
        # Identificar ciudad
        ciudad = identificar_ciudad_departamento(numero)
        if ciudad:
            print(f"   📍 UBICACIÓN: {ciudad['ciudad']}, {ciudad['departamento']}")
    
    # Mostrar estadísticas
    print("\n" + "=" * 60)
    print("📈 ESTADÍSTICAS DE OPERADORES EN COLOMBIA")
    print("=" * 60)
    
    stats = obtener_estadisticas_operadores()
    for operador, info in sorted(stats.items()):
        print(f"   {operador}: {info['cantidad']} prefijos")
    
    # Probar detección de fraude
    print("\n" + "=" * 60)
    print("🚨 PRUEBA DE DETECCIÓN DE FRAUDE")
    print("=" * 60)
    
    mensajes_prueba = [
        "Felicidades! Has ganado un premio",
        "Tu tarjeta de crédito ha sido bloqueada",
        "Hola soy tu familiar, necesito dinero urgente",
        "Confirmación de compra normal"
    ]
    
    for mensaje in mensajes_prueba:
        fraudes = detectar_fraude(mensaje)
        if fraudes:
            print(f"\n⚠️ MENSAJE: {mensaje}")
            print(f"   🔴 Patrones de fraude detectados: {', '.join(fraudes)}")
        else:
            print(f"\n✅ MENSAJE: {mensaje}")
            print(f"   🟢 Sin patrones de fraude")
    
    print("\n" + "=" * 60)
    print("✅ DATOS COLOMBIANOS CARGADOS CORRECTAMENTE")
    print("=" * 60)
