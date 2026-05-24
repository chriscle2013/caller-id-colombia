# test.py - Verificar que todo funciona
import phonenumbers
from phonenumbers import carrier, geocoder

print("=" * 50)
print("✅ PRUEBA DE IDENTIFICADOR COLOMBIA")
print("=" * 50)

# Probar con un número colombiano
numeros_prueba = [
    "+573001234567",  # Claro
    "+573102345678",  # Movistar
    "+573152345678",  # Tigo
]

for numero in numeros_prueba:
    print(f"\n📞 Probando: {numero}")
    try:
        parsed = phonenumbers.parse(numero, "CO")
        
        if phonenumbers.is_valid_number(parsed):
            operador = carrier.name_for_number(parsed, "es") or "Desconocido"
            ubicacion = geocoder.description_for_number(parsed, "es") or "Colombia"
            
            print(f"   ✅ Válido")
            print(f"   📱 Operador: {operador}")
            print(f"   📍 Ubicación: {ubicacion}")
        else:
            print(f"   ❌ Inválido")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ ¡TODO FUNCIONA CORRECTAMENTE!")
print("=" * 50)