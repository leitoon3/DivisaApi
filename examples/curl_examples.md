# Ejemplos CURL - API con Múltiples Formatos

La API ahora soporta **JSON**, **CSV** y **XML** como formatos de respuesta. Puedes especificar el formato de dos maneras:

## 1. Usando Parámetro de Query `?format=`

### JSON (Por defecto)
```bash
curl "http://localhost:5000/api/rates"
curl "http://localhost:5000/api/rates?format=json"
```

### CSV 
```bash
curl "http://localhost:5000/api/rates?format=csv"
curl "http://localhost:5000/api/rates/usd?format=csv"
```

### XML
```bash
curl "http://localhost:5000/api/rates?format=xml"
curl "http://localhost:5000/api/rates/eur?format=xml"
```

## 2. Usando Header Accept

### CSV con Accept Header
```bash
curl -H "Accept: text/csv" "http://localhost:5000/api/rates"
curl -H "Accept: text/csv" "http://localhost:5000/api/rates/usd"
```

### XML con Accept Header
```bash
curl -H "Accept: application/xml" "http://localhost:5000/api/rates"
curl -H "Accept: text/xml" "http://localhost:5000/api/rates/eur"
```

## Ejemplos de Respuestas

### 1. JSON (Por defecto)
```bash
curl "http://localhost:5000/api/rates/usd"
```
**Respuesta:**
```json
{
  "success": true,
  "currency": "USD",
  "rate": 129.0535,
  "date_published": "Jueves, 07 Agosto 2025",
  "last_updated": "2025-08-07T18:39:40.698805",
  "timestamp": "2025-08-07T18:50:30.123456",
  "source": "Banco Central de Venezuela (BCV) - Cached"
}
```

### 2. CSV
```bash
curl "http://localhost:5000/api/rates/usd?format=csv"
```
**Respuesta:**
```csv
Currency,Rate,Date_Published,Last_Updated,Timestamp
USD,129.0535,Jueves, 07 Agosto 2025,2025-08-07T18:39:40.698805,2025-08-07T18:50:30.123456
```

### 3. XML
```bash
curl "http://localhost:5000/api/rates/usd?format=xml"
```
**Respuesta:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bcv_rate>
    <success>true</success>
    <currency>USD</currency>
    <rate>129.0535</rate>
    <date_published>Jueves, 07 Agosto 2025</date_published>
    <last_updated>2025-08-07T18:39:40.698805</last_updated>
    <timestamp>2025-08-07T18:50:30.123456</timestamp>
    <source>Banco Central de Venezuela (BCV) - Cached</source>
</bcv_rate>
```

## Casos de Uso Prácticos

### 1. Importar a Excel/Google Sheets
```bash
# Descargar todas las tasas como CSV
curl "http://localhost:5000/api/rates?format=csv" -o tasas_bcv.csv

# Descargar solo USD como CSV
curl "http://localhost:5000/api/rates/usd?format=csv" -o usd_rate.csv
```

### 2. Integración con Sistemas XML
```bash
# Para sistemas que procesan XML
curl -H "Accept: application/xml" "http://localhost:5000/api/rates" > tasas_bcv.xml
```

### 3. Scripts de Monitoreo
```bash
#!/bin/bash
# Script que obtiene tasa USD y la procesa
USD_RATE=$(curl -s "http://localhost:5000/api/rates/usd" | jq -r '.rate')
echo "Tasa actual USD: $USD_RATE VES"
```

### 4. Integración con Python pandas
```python
import pandas as pd

# Leer CSV directamente desde la API
url = "http://tu-servidor.com/api/rates?format=csv"
df = pd.read_csv(url)
print(df)
```

### 5. Procesamiento con jq (JSON)
```bash
# Extraer solo las tasas
curl -s "http://localhost:5000/api/rates" | jq '.data.rates'

# Obtener solo tasa USD
curl -s "http://localhost:5000/api/rates/usd" | jq '.rate'
```

## Todos los Endpoints Soportan Múltiples Formatos

### Endpoints Principales
```bash
# Todas las tasas
curl "http://localhost:5000/api/rates?format=csv"
curl "http://localhost:5000/api/rates?format=xml"

# Tasas específicas
curl "http://localhost:5000/api/rates/usd?format=csv"
curl "http://localhost:5000/api/rates/eur?format=xml"
curl "http://localhost:5000/api/rates/cny?format=csv"

# Estado del sistema
curl "http://localhost:5000/api/status?format=csv"
curl "http://localhost:5000/api/status?format=xml"
```

### POST Endpoints (también soportan formatos)
```bash
# Forzar actualización con respuesta en XML
curl -X POST "http://localhost:5000/api/update?format=xml"
```

## Guardar Respuestas en Archivos

### CSV para análisis en Excel
```bash
# Todas las tasas
curl "http://localhost:5000/api/rates?format=csv" -o "tasas_$(date +%Y%m%d).csv"

# Solo USD histórico
curl "http://localhost:5000/api/rates/usd?format=csv" -o "usd_$(date +%Y%m%d_%H%M).csv"
```

### XML para sistemas empresariales
```bash
curl "http://localhost:5000/api/rates?format=xml" -o tasas_bcv.xml
```

## Automatización con Cron

### Script diario para recopilar datos
```bash
#!/bin/bash
# archivo: /home/usuario/get_rates.sh

DATE=$(date +%Y%m%d)
API_URL="http://tu-servidor.com"

# Descargar en todos los formatos
curl "$API_URL/api/rates?format=csv" -o "/data/tasas_$DATE.csv"
curl "$API_URL/api/rates?format=xml" -o "/data/tasas_$DATE.xml"
curl "$API_URL/api/rates" -o "/data/tasas_$DATE.json"

echo "Tasas descargadas para $DATE"
```

### Crontab para ejecutar diariamente
```bash
# Agregar a crontab (crontab -e)
0 9 * * * /home/usuario/get_rates.sh
```

## Ventajas de Cada Formato

### JSON
- ✅ Fácil de parsear en aplicaciones web
- ✅ Soporte nativo en JavaScript
- ✅ Estructura jerárquica clara
- 🎯 **Ideal para**: APIs, aplicaciones web, JavaScript

### CSV
- ✅ Compatible con Excel y Google Sheets
- ✅ Fácil análisis estadístico
- ✅ Archivos pequeños y eficientes
- 🎯 **Ideal para**: Análisis de datos, reportes, Excel

### XML
- ✅ Compatible con sistemas empresariales
- ✅ Estructura validable con esquemas
- ✅ Soporte en muchos lenguajes legacy
- 🎯 **Ideal para**: Integración empresarial, sistemas XML, SOAP

## Códigos de Estado HTTP

La API mantiene los mismos códigos de estado en todos los formatos:

- `200` - Éxito
- `404` - Divisa no encontrada  
- `429` - Rate limit excedido (espera 10 segundos)
- `500` - Error interno del servidor
- `503` - Servicio no disponible (problemas con BCV)

## Notas Importantes

1. **Rate Limiting**: El límite de 10 segundos por IP aplica para todos los formatos
2. **Cache**: Los datos vienen del mismo cache independientemente del formato
3. **Consistencia**: Los datos son idénticos en todos los formatos
4. **Headers**: Los headers Content-Type se ajustan automáticamente:
   - JSON: `application/json`
   - CSV: `text/csv` 
   - XML: `application/xml`