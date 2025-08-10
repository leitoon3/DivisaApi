# 🚀 DivisaAPI - API de Tipos de Cambio del BCV

**Versión:** 1.1.0  
**Última Actualización:** 10 de Agosto, 2025

Una API moderna y robusta para obtener tipos de cambio del Banco Central de Venezuela (BCV) con interfaz web integrada y sistema de configuración flexible.

## ✨ Características Principales

### 🔌 **API REST Completa**
- **GET /api/rates** - Obtener todos los tipos de cambio
- **GET /api/convert** - Convertir entre divisas
- **GET /api/status** - Estado del sistema y métricas
- **GET /api/update** - Forzar actualización manual
- **GET /api/metrics** - Estadísticas de uso de la API

### 🌐 **Interfaz Web Moderna**
- **Diseño Oscuro Atractivo** con gradientes y animaciones
- **Convertidor de Divisas Integrado** con selección de monedas
- **Botones de Copia Rápida** para tasas y endpoints
- **Diseño Responsivo** optimizado para móviles y desktop
- **Sistema de Iconos Feather** con fallback robusto
- **Feedback Visual** para todas las operaciones

### 🗄️ **Soporte Multi-Base de Datos**
- **PostgreSQL** - Para entornos de producción
- **MariaDB/MySQL** - Para entornos empresariales
- **SQLite** - Para desarrollo y testing
- **Pool de Conexiones** configurable
- **Migración Automática** de esquemas

### ⚡ **Funcionalidades Avanzadas**
- **Actualización Automática** cada 30 minutos (configurable)
- **Rate Limiting** para prevenir abuso
- **Métricas de API** en tiempo real
- **Logging Configurable** por entorno
- **Manejo de Errores Robusto**
- **Timeout Inteligente** para requests

## 🚀 Instalación Rápida

### 1. **Clonar el Proyecto**
```bash
git clone <repository-url>
cd DivisaAPI
```

### 2. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 3. **Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con tu configuración
nano .env
```

### 4. **Ejecutar la Aplicación**
```bash
python app.py
```

## ⚙️ Configuración

### **Variables de Entorno Principales**

```bash
# Entorno
FLASK_ENV=development
FLASK_DEBUG=true

# Base de Datos
DB_TYPE=mariadb          # mariadb, postgresql, sqlite
DB_HOST=192.168.0.201
DB_PORT=3306
DB_NAME=divisa_api
DB_USER=raton
DB_PASSWORD=ques1

# Aplicación
UPDATE_INTERVAL_MINUTES=30  # Actualización automática
RATE_LIMIT_SECONDS=10       # Rate limiting
REQUEST_TIMEOUT=30          # Timeout para BCV
```

### **Configuraciones por Base de Datos**

#### **MariaDB/MySQL**
```bash
DB_TYPE=mariadb
DB_HOST=192.168.0.201
DB_PORT=3306
DB_NAME=divisa_api
DB_USER=raton
DB_PASSWORD=ques1
```

#### **PostgreSQL**
```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=divisa_api
DB_USER=postgres
DB_PASSWORD=password
```

#### **SQLite**
```bash
DB_TYPE=sqlite
DB_NAME=divisa_api.db
```

## 🌟 Interfaz Web

### **Características de la UI**
- **Tema Oscuro Moderno** con gradientes azules
- **Elementos Flotantes Animados** en el fondo
- **Tarjetas de Divisas** con efectos hover
- **Convertidor Integrado** con validación en tiempo real
- **Botones de Copia** para tasas y endpoints de API
- **Diseño Responsivo** para todos los dispositivos

### **Funcionalidades del Convertidor**
- **Selección de Monedas** con todas las divisas del BCV
- **Cálculos Locales** usando tasas cargadas
- **Formato Inteligente** de números por moneda
- **Ejemplos Claros** de conversiones
- **Botón de Copia** para resultados

## 📊 Endpoints de la API

### **GET /api/rates**
Obtiene todos los tipos de cambio disponibles.

**Respuesta:**
```json
{
  "rates": {
    "USD": 131.24,
    "EUR": 142.56,
    "CNY": 18.23
  },
  "base_currency": "VES",
  "last_updated": "2024-12-19T10:30:00"
}
```

### **GET /api/convert**
Convierte entre divisas.

**Parámetros:**
- `amount`: Cantidad a convertir
- `from`: Moneda origen
- `to`: Moneda destino

**Ejemplo:**
```
/api/convert?amount=10&from=USD&to=VES
```

### **GET /api/status**
Estado del sistema y última actualización.

### **GET /api/update**
Fuerza una actualización manual desde el BCV.

## 🔧 Desarrollo

### **Estructura del Proyecto**
```
DivisaAPI/
├── app.py                 # Aplicación principal Flask
├── config.py             # Sistema de configuración
├── models.py             # Modelos de base de datos
├── database_service.py   # Servicio de base de datos
├── bcv_scraper.py       # Scraper del BCV
├── templates/
│   └── index.html       # Interfaz web principal
├── requirements.txt      # Dependencias Python
├── env.example          # Ejemplo de variables de entorno
└── README.md            # Este archivo
```

### **Ejecutar en Modo Desarrollo**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python app.py
```

### **Probar la Configuración**
```bash
python test_config.py
```

## 📈 Monitoreo y Métricas

### **Métricas Disponibles**
- **Tiempo de Respuesta** por endpoint
- **Códigos de Estado** HTTP
- **Uso de la API** por IP
- **Logs de Actualización** del BCV
- **Estado de la Base de Datos**

### **Logs del Sistema**
- **Nivel Configurable** (DEBUG, INFO, WARNING, ERROR)
- **Logs de Actualización** automática
- **Errores de Scraping** del BCV
- **Métricas de Rendimiento**

## 🚀 Despliegue

### **Requisitos del Servidor**
- **Python 3.8+**
- **Base de datos** (MariaDB, PostgreSQL o SQLite)
- **Memoria RAM**: 512MB mínimo
- **Almacenamiento**: 100MB mínimo

### **Variables de Producción**
```bash
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=WARNING
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### **Docker (Próximamente)**
```bash
# Dockerfile y docker-compose.yml en desarrollo
docker build -t divisa-api .
docker run -p 5000:5000 divisa-api
```

## 🤝 Contribuir

### **Cómo Contribuir**
1. **Fork** del proyecto
2. **Crear** una rama para tu feature
3. **Commit** tus cambios
4. **Push** a la rama
5. **Crear** un Pull Request

### **Estándares de Código**
- **PEP 8** para Python
- **Docstrings** para todas las funciones
- **Type Hints** donde sea posible
- **Tests** para nuevas funcionalidades

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Banco Central de Venezuela** por proporcionar los datos de tipos de cambio
- **Comunidad Python** por las librerías utilizadas
- **Contribuidores** del proyecto

## 📞 Soporte

- **Issues**: Crear un issue en GitHub
- **Documentación**: Revisar este README y el CHANGELOG
- **Configuración**: Ver `env.example` y `config.py`

---


**DivisaAPI v1.1.0** - Una API moderna para tipos de cambio del BCV 🇻🇪 
