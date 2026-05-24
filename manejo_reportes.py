# manejo_reportes.py - Funciones para gestionar reportes de spam
import sqlite3
from datetime import datetime
import re

def limpiar_numero(numero):
    """Limpia el número para usarlo como clave en la BD"""
    solo_digitos = re.sub(r'\D', '', numero)
    if solo_digitos.startswith('57'):
        solo_digitos = solo_digitos[2:]
    return solo_digitos

def reportar_spam(numero, categoria="spam", comentario="", ip=""):
    """Reporta un número como spam"""
    numero_limpio = limpiar_numero(numero)
    
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    
    # Verificar si ya existe
    cursor.execute('SELECT reportes, riesgo FROM numeros_reportados WHERE numero = ?', (numero_limpio,))
    existente = cursor.fetchone()
    
    if existente:
        nuevos_reportes = existente[0] + 1
        
        # Calcular nuevo riesgo
        if nuevos_reportes >= 10:
            nuevo_riesgo = "high"
        elif nuevos_reportes >= 5:
            nuevo_riesgo = "medium"
        else:
            nuevo_riesgo = "low"
        
        # Actualizar
        cursor.execute('''
            UPDATE numeros_reportados 
            SET reportes = ?, ultimo_reporte = ?, riesgo = ?, categoria = ?
            WHERE numero = ?
        ''', (nuevos_reportes, datetime.now().isoformat(), nuevo_riesgo, categoria, numero_limpio))
    else:
        # Insertar nuevo
        cursor.execute('''
            INSERT INTO numeros_reportados (numero, reportes, ultimo_reporte, categoria, riesgo)
            VALUES (?, 1, ?, ?, 'low')
        ''', (numero_limpio, datetime.now().isoformat(), categoria))
    
    # Guardar reporte individual
    cursor.execute('''
        INSERT INTO reportes (numero, categoria, comentario, ip, fecha)
        VALUES (?, ?, ?, ?, ?)
    ''', (numero_limpio, categoria, comentario, ip, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

def verificar_spam(numero):
    """Verifica si un número ha sido reportado como spam"""
    numero_limpio = limpiar_numero(numero)
    
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT reportes, riesgo, categoria, ultimo_reporte 
        FROM numeros_reportados 
        WHERE numero = ?
    ''', (numero_limpio,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            'es_spam': True,
            'reportes': resultado[0],
            'riesgo': resultado[1],
            'categoria': resultado[2],
            'ultimo_reporte': resultado[3]
        }
    else:
        return {'es_spam': False, 'reportes': 0}

def obtener_top_spam(limite=10):
    """Obtiene los números más reportados"""
    conn = sqlite3.connect('reportes_spam.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT numero, reportes, riesgo, categoria 
        FROM numeros_reportados 
        ORDER BY reportes DESC 
        LIMIT ?
    ''', (limite,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    return [{'numero': r[0], 'reportes': r[1], 'riesgo': r[2], 'categoria': r[3]} for r in resultados]

# Prueba
if __name__ == "__main__":
    print("=== PRUEBA DEL SISTEMA DE REPORTES ===\n")
    
    # Verificar número
    numero = "3001234567"
    print(f"📞 Verificando: {numero}")
    resultado = verificar_spam(numero)
    print(f"   ¿Es spam? {resultado['es_spam']}")
    print(f"   Reportes: {resultado['reportes']}")
    
    # Reportar spam
    print(f"\n📝 Reportando {numero} como spam...")
    reportar_spam(numero, "telemarketing", "Llaman todos los días")
    
    # Verificar nuevamente
    resultado = verificar_spam(numero)
    print(f"\n📞 Verificando nuevamente: {numero}")
    print(f"   ¿Es spam? {resultado['es_spam']}")
    print(f"   Reportes: {resultado['reportes']}")
    print(f"   Riesgo: {resultado['riesgo']}")
    
    # Mostrar top spam
    print("\n🏆 TOP NÚMEROS MÁS REPORTADOS:")
    for spam in obtener_top_spam():
        print(f"   {spam['numero']} - {spam['reportes']} reportes ({spam['riesgo']})")
