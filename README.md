# 📱 Identificador de Llamadas Colombia

API gratuita para identificar números de teléfono en Colombia.

## Características

- 🇨🇴 Identifica operadores colombianos (Claro, Movistar, Tigo, WOM, Avantel, Virgin, ETB, Flash, Móvil Éxito)
- 📍 Detecta ciudades y departamentos
- 🚨 Lista de números de emergencia
- 📊 Sistema de reportes de spam colaborativo

## Endpoints

- `POST /identify` - Identificar número
- `POST /report` - Reportar spam
- `GET /emergencias` - Ver números de emergencia
- `GET /estadisticas` - Estadísticas de operadores

## Uso

```bash
curl -X POST https://tu-api.onrender.com/identify \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573001234567"}'
