# Ejemplos de Integración - API de Tipos de Cambio BCV

Esta carpeta contiene ejemplos de cómo integrar la API de tipos de cambio BCV en diferentes lenguajes de programación y aplicaciones.

## Endpoints Disponibles

### Endpoints Principales
- `GET /api/rates` - Obtener todas las tasas de cambio
- `GET /api/rates/{currency}` - Obtener tasa específica (USD, EUR, CNY, TRY, RUB)
- `GET /api/rates/usd` - Acceso directo al dólar
- `GET /api/rates/eur` - Acceso directo al euro

### Endpoints de Sistema
- `GET /api/status` - Estado del sistema y logs de actualización
- `GET /api/health` - Verificación de salud del servicio
- `POST /api/update` - Forzar actualización desde BCV (limitado por rate limiting)

## Características de la API

✅ **Cache inteligente**: Datos servidos desde PostgreSQL para respuestas ultra-rápidas
✅ **Actualización automática**: Cada 30 minutos desde el sitio oficial del BCV
✅ **Rate limiting**: 10 segundos entre solicitudes por IP para evitar abuso
✅ **Fallback robusto**: Si BCV no responde, sirve datos del cache
✅ **Formato JSON**: Respuestas consistentes y fáciles de parsear

## Ejemplos Disponibles

### 1. Python (`python_client.py`)
Cliente completo con funciones de conversión de divisas:

```bash
python examples/python_client.py
```

**Características:**
- Clase `BCVAPIClient` para manejo completo de la API
- Funciones de conversión automática entre VES y divisas extranjeras
- Manejo de errores robusto
- Formateo automático de números

### 2. JavaScript (`javascript_client.js`)
Compatible con navegador y Node.js:

```javascript
const client = new BCVAPIClient('https://tu-servidor.com');
const rates = await client.getAllRates();
```

**Características:**
- Compatible con navegadores modernos y Node.js
- Funciones asíncronas con async/await
- Calculadora en tiempo real para interfaces web
- Manejo automático de CORS

### 3. PHP (`php_client.php`)
Cliente para aplicaciones web PHP:

```bash
php examples/php_client.php
```

**Características:**
- Compatible con PHP 7.4+
- Funciones de formateo de moneda
- Conversiones automáticas
- Manejo de errores con try/catch

## Casos de Uso Comunes

### 1. App de Conversión de Divisas
```python
client = BCVAPIClient("https://tu-api.com")

# Convertir $100 USD a bolívares
conversion = client.convert_currency(100, "USD", "VES")
print(f"$100 USD = {conversion['converted_amount']:,} VES")
```

### 2. Widget de Tasas en Sitio Web
```javascript
const client = new BCVAPIClient('https://tu-api.com');
const rates = await client.getAllRates();

document.getElementById('usd-rate').textContent = 
    rates.data.rates.USD.toLocaleString() + ' VES';
```

### 3. Sistema de E-commerce
```php
$client = new BCVAPIClient('https://tu-api.com');
$usdRate = $client->getCurrencyRate('USD');
$priceInVes = $priceInUsd * $usdRate['rate'];
```

### 4. Dashboard de Monitoreo
```python
# Obtener estado del sistema
status = client.get_status()
print(f"Última actualización: {status['last_update']}")
print(f"Tasas disponibles: {status['rates_available']}")
```

## Configuración de Producción

### 1. Cambiar URL Base
En todos los ejemplos, reemplaza:
```
http://localhost:5000
```
Por la URL de tu servidor desplegado:
```
https://tu-dominio.com
```

### 2. Manejo de Rate Limiting
La API tiene límite de 1 solicitud cada 10 segundos por IP. Para aplicaciones de alto tráfico:

- Implementa cache local en tu aplicación
- Usa un proxy/load balancer con múltiples IPs
- Considera actualizar las tasas cada pocos minutos en lugar de cada solicitud

### 3. Manejo de Errores
Siempre verifica errores en las respuestas:

```python
result = client.get_currency_rate('USD')
if 'error' in result:
    # Manejar error - usar cache local, mostrar mensaje, etc.
    print(f"Error: {result['error']}")
else:
    # Usar los datos
    print(f"Tasa USD: {result['rate']}")
```

## Estructura de Respuestas

### Respuesta Exitosa (Tasa Individual)
```json
{
    "success": true,
    "currency": "USD",
    "rate": 129.0535,
    "date_published": "Jueves, 07 Agosto 2025",
    "last_updated": "2025-08-07T18:39:40.698805",
    "timestamp": "2025-08-07T18:47:12.123456",
    "source": "Banco Central de Venezuela (BCV) - Cached"
}
```

### Respuesta Exitosa (Todas las Tasas)
```json
{
    "success": true,
    "data": {
        "rates": {
            "USD": 129.0535,
            "EUR": 150.24666577,
            "CNY": 15.0,
            "TRY": 5.0,
            "RUB": 3.0
        },
        "date": "Jueves, 07 Agosto 2025",
        "currencies_available": ["USD", "EUR", "CNY", "TRY", "RUB"],
        "base_currency": "VES",
        "last_updated": "2025-08-07T18:39:40.698805"
    },
    "source": "Banco Central de Venezuela (BCV) - Cached",
    "timestamp": "2025-08-07T18:47:12.123456"
}
```

### Respuesta de Error
```json
{
    "error": "Currency not found",
    "message": "EUR exchange rate not available",
    "timestamp": "2025-08-07T18:47:12.123456"
}
```

## Ventajas para Desarrolladores

1. **Sin límites del BCV**: Tu API hace cache de los datos, evitando bloqueos del sitio oficial
2. **Respuestas rápidas**: Datos servidos desde base de datos local en milisegundos
3. **Datos siempre disponibles**: Fallback a cache si BCV está inaccesible
4. **API REST estándar**: Fácil de integrar en cualquier lenguaje
5. **Actualizaciones automáticas**: Los datos se mantienen frescos sin intervención manual

## Soporte

Para más información sobre la API, consulta la documentación interactiva en:
`https://tu-servidor.com/`