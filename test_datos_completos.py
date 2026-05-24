# test_datos_completos.py - Probar datos mejorados de Colombia
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("🇨🇴 PROBANDO DATOS COMPLETOS DE COLOMBIA")
print("=" * 60)

# Probar números de emergencia
emergencias = ["123", "125", "132", "144", "147"]
print("\n🚨 PROBANDO NÚMEROS DE EMERGENCIA:")
for num in emergencias:
    response = requests.post(f"{API_URL}/identify", json={"phone": num})
    data = response.json()
    if data.get('is_emergency'):
        print(f"   ✅ {num}: {data.get('emergency_info', 'Emergencia')[:50]}")

# Probar nuevos operadores
nuevos_operadores = [
    ("+573601234567", "Flash"),
    ("+573701234567", "Móvil Éxito"),
    ("+573551234567", "ETB Móvil"),
]

print("\n📱 PROBANDO NUEVOS OPERADORES:")
for num, esperado in nuevos_operadores:
    response = requests.post(f"{API_URL}/identify", json={"phone": num})
    data = response.json()
    operador = data.get('carrier', '')
    print(f"   {num}: {operador} {'✅' if esperado in operador else '❌'}")

# Probar endpoint de estadísticas
print("\n📊 ESTADÍSTICAS DE OPERADORES:")
response = requests.get(f"{API_URL}/estadisticas")
stats = response.json()
for operador, cantidad in sorted(stats.items())[:5]:
    print(f"   {operador}: {cantidad} prefijos")

# Probar endpoint de emergencias
print("\n📞 LISTA DE EMERGENCIAS:")
response = requests.get(f"{API_URL}/emergencias")
emergencias_lista = response.json()
for codigo, nombre in list(emergencias_lista.items())[:5]:
    print(f"   {codigo}: {nombre[:40]}...")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
