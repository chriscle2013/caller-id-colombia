# test_reportes.py - Probar sistema de reportes
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("📝 PROBANDO SISTEMA DE REPORTES")
print("=" * 60)

# 1. Identificar un número
numero = "3001234567"
print(f"\n1️⃣ Identificando {numero}")
response = requests.post(f"{API_URL}/identify", json={"phone": numero})
print(f"   Resultado: {response.json()}")

# 2. Reportar como spam
print(f"\n2️⃣ Reportando {numero} como spam")
reporte = {
    "phone": numero,
    "category": "telemarketing",
    "comment": "Llaman todos los días ofreciendo planes"
}
response = requests.post(f"{API_URL}/report", json=reporte)
print(f"   Resultado: {response.json()}")

# 3. Verificar nuevamente (debe mostrar reportes)
print(f"\n3️⃣ Verificando {numero} nuevamente")
response = requests.post(f"{API_URL}/identify", json={"phone": numero})
data = response.json()
print(f"   ¿Reportado? {data.get('is_reported', False)}")
print(f"   Reportes: {data.get('reports', 0)}")
print(f"   Riesgo: {data.get('spam_risk', 'unknown')}")

# 4. Verificar con endpoint específico
print(f"\n4️⃣ Verificando con /check-spam")
response = requests.get(f"{API_URL}/check-spam/{numero}")
print(f"   Resultado: {response.json()}")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
