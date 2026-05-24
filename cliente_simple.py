# cliente_simple.py - Cliente interactivo para probar identificación
import requests
import sys

API_URL = "http://localhost:8000"

def identificar_numero():
    print("\n" + "=" * 50)
    print("📱 IDENTIFICADOR DE LLAMADAS COLOMBIA")
    print("=" * 50)
    
    while True:
        print("\n🔍 Ingresa un número colombiano:")
        print("   (Ej: 3001234567, +573001234567)")
        print("   (Escribe 'salir' para terminar)")
        
        numero = input("\n📞 Número: ").strip()
        
        if numero.lower() == 'salir':
            print("\n👋 ¡Hasta luego!")
            break
        
        if not numero:
            print("❌ Por favor ingresa un número")
            continue
        
        print("\n🔎 Identificando...")
        
        try:
            response = requests.post(
                f"{API_URL}/identify",
                json={"phone": numero},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid'):
                    print("\n" + "─" * 40)
                    print("✅ RESULTADO DE IDENTIFICACIÓN")
                    print("─" * 40)
                    print(f"📞 Número: {data.get('national', 'N/A')}")
                    print(f"🏷️  Tipo: {data.get('type', 'N/A')}")
                    print(f"📡 Operador: {data.get('carrier', 'N/A')}")
                    print(f"📍 Ubicación: {data.get('location', 'N/A')}")
                    
                    riesgo = data.get('spam_risk', 'low')
                    if riesgo == 'low':
                        print(f"🟢 Nivel de riesgo: BAJO")
                        print("✅ Número aparentemente seguro")
                    elif riesgo == 'medium':
                        print(f"🟠 Nivel de riesgo: MEDIO")
                        print("⚠️ Ten precaución con este número")
                    else:
                        print(f"🔴 Nivel de riesgo: ALTO")
                        print("🚨 ¡POSIBLE SPAM! No contestes")
                    print("─" * 40)
                else:
                    print(f"\n❌ {data.get('error', 'Número inválido')}")
            else:
                print(f"\n❌ Error del servidor: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: No se pudo conectar al servidor")
            print("💡 ¿Ejecutaste 'python app.py' en otra terminal?")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    identificar_numero()
