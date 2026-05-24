# test_api.py - Probar la API de identificación
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 60)
print("🧪 PROBANDO API IDENTIFICADOR COLOMBIA")
print("=" * 60)

# Lista de números colombianos para probar
numeros_prueba = [
    "+573001234567",   # Claro
    "+573102345678",   # Movistar  
    "+573152345678",   # Tigo
    "3001234567",      # Sin código país
    "3201234567",      # WOM
    "6012345678",      # Número fijo Bogotá
]

for numero in numeros_prueba:
    print(f"\n📞 Probando: {numero}")
    
    try:
        response = requests.post(
            f"{API_URL}/identify",
            json={"phone": numero},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('valid'):
                print(f"   ✅ NÚMERO VÁLIDO")
                print(f"   📱 Formato: {data.get('national', 'N/A')}")
                print(f"   🏷️  Tipo: {data.get('type', 'N/A')}")
                print(f"   📡 Operador: {data.get('carrier', 'N/A')}")
                print(f"   📍 Ubicación: {data.get('location', 'N/A')}")
                
                # Icono según riesgo
                riesgo = data.get('spam_risk', 'low')
                if riesgo == 'low':
                    print(f"   🟢 Riesgo: Bajo")
                elif riesgo == 'medium':
                    print(f"   🟠 Riesgo: Medio")
                else:
                    print(f"   🔴 Riesgo: Alto")
            else:
                print(f"   ❌ {data.get('error', 'Número inválido')}")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ No se pudo conectar al servidor")
        print(f"   💡 ¿Ejecutaste 'python app.py' en otra terminal?")
        break
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)

