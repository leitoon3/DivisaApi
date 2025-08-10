# 🚀 DivisaAPI PWA - Progressive Web App

## 📱 ¿Qué es una PWA?

Una **Progressive Web App (PWA)** es una aplicación web que se comporta como una aplicación nativa en dispositivos móviles y desktop. DivisaAPI ahora incluye funcionalidades PWA que permiten:

- ✅ **Instalación** en dispositivos móviles y desktop
- ✅ **Funcionamiento offline** con cache inteligente
- ✅ **Sincronización en background** de tipos de cambio
- ✅ **Notificaciones push** (futuras implementaciones)
- ✅ **Experiencia nativa** con iconos y splash screens

## 🎯 Características PWA de DivisaAPI

### 🔧 **Funcionalidades Principales**

1. **Instalación Automática**
   - Banner de instalación que aparece automáticamente
   - Botón flotante de instalación
   - Compatible con Chrome, Edge, Firefox y Safari

2. **Cache Offline Inteligente**
   - Cache de archivos estáticos (CSS, JS, iconos)
   - Cache de respuestas de API
   - Estrategia "Network First" con fallback a cache
   - Actualización automática de cache

3. **Service Worker Avanzado**
   - Gestión de cache automática
   - Sincronización en background
   - Actualizaciones automáticas de la aplicación
   - Manejo de errores y reintentos

4. **Interfaz Adaptativa**
   - Indicador de estado online/offline
   - Notificaciones de actualización
   - Modo standalone (sin barra de navegación)
   - Soporte para gestos táctiles

## 📁 Estructura de Archivos PWA

```
static/
├── manifest.json          # Configuración de la PWA
├── sw.js                 # Service Worker
├── css/
│   └── app.css          # Estilos específicos de PWA
├── js/
│   └── app.js           # JavaScript principal de PWA
└── icons/                # Iconos en diferentes tamaños
    ├── icon-72x72.png
    ├── icon-96x96.png
    ├── icon-128x128.png
    ├── icon-144x144.png
    ├── icon-152x152.png
    ├── icon-192x192.png
    ├── icon-384x384.png
    └── icon-512x512.png
```

## 🚀 Cómo Usar la PWA

### **1. Instalación Automática**

La PWA mostrará automáticamente un banner de instalación después de unos segundos de uso:

```
┌─────────────────────────────────────┐
│ 📱 Instalar DivisaAPI              │
│ Accede rápidamente a los tipos     │
│ de cambio del BCV                  │
│                                     │
│ [Instalar] [Más tarde]             │
└─────────────────────────────────────┘
```

### **2. Instalación Manual**

Si el banner no aparece, puedes instalar manualmente:

- **Chrome/Edge**: Click en el icono de instalación en la barra de direcciones
- **Firefox**: Click en el icono de instalación en la barra de direcciones
- **Safari**: Compartir → "Añadir a pantalla de inicio"

### **3. Botón Flotante**

Un botón flotante azul aparecerá en la esquina inferior derecha cuando la instalación esté disponible.

## 🔄 Funcionamiento Offline

### **Cache Estratégico**

- **Archivos Estáticos**: Cache permanente (CSS, JS, iconos)
- **Página Principal**: Cache con actualización automática
- **API Endpoints**: Cache temporal con estrategia "Network First"
- **Datos de Tipos de Cambio**: Cache de 24 horas

### **Estrategias de Cache**

1. **Cache First**: Para archivos estáticos
2. **Network First**: Para datos de API
3. **Stale While Revalidate**: Para contenido dinámico

### **Sincronización en Background**

- Actualización automática de tipos de cambio
- Sincronización cuando el dispositivo vuelve a estar online
- Reintentos automáticos en caso de fallo

## 📱 Experiencia Móvil

### **Modo Standalone**

Una vez instalada, la PWA se ejecuta en modo standalone:

- Sin barra de navegación del navegador
- Icono personalizado en el launcher
- Splash screen personalizado
- Comportamiento nativo

### **Gestos Táctiles**

- Swipe para navegar entre secciones
- Pull-to-refresh para actualizar datos
- Tap para acciones principales
- Long press para opciones adicionales

## ⚙️ Configuración Avanzada

### **Variables de Entorno PWA**

```bash
# Configuración de notificaciones push (opcional)
VAPID_PUBLIC_KEY=tu_clave_publica_vapid
VAPID_PRIVATE_KEY=tu_clave_privada_vapid

# Configuración de cache
PWA_CACHE_SIZE=50MB
PWA_UPDATE_INTERVAL=30
```

### **Personalización del Manifest**

Edita `static/manifest.json` para personalizar:

- Nombre y descripción de la app
- Colores del tema
- Iconos personalizados
- Shortcuts de navegación
- Categorías de la app store

## 🧪 Testing de la PWA

### **Herramientas de Desarrollo**

1. **Chrome DevTools**
   - Application tab → Service Workers
   - Application tab → Manifest
   - Application tab → Storage

2. **Lighthouse PWA Audit**
   - Performance
   - Accessibility
   - Best Practices
   - SEO
   - **PWA Score**

### **Verificación de Funcionalidades**

```bash
# Ejecutar validación de configuración
python pwa_config.py

# Verificar archivos PWA
python -c "from pwa_config import PWAConfig; print(PWAConfig.validate_config())"
```

## 🔍 Troubleshooting

### **Problemas Comunes**

1. **PWA no se instala**
   - Verificar HTTPS (requerido para PWA)
   - Verificar manifest.json válido
   - Verificar Service Worker registrado

2. **Cache no funciona**
   - Verificar Service Worker activo
   - Limpiar cache del navegador
   - Verificar rutas en sw.js

3. **Iconos no se muestran**
   - Verificar rutas en manifest.json
   - Verificar tamaños de iconos
   - Verificar formato PNG válido

### **Logs de Debug**

```javascript
// En la consola del navegador
console.log('PWA Status:', checkPWAStatus());

// Verificar Service Worker
navigator.serviceWorker.getRegistrations().then(registrations => {
    console.log('SW Registrations:', registrations);
});
```

## 📊 Métricas y Analytics

### **Eventos Rastreados**

- Instalación de PWA
- Uso offline vs online
- Tiempo de carga desde cache
- Errores de Service Worker
- Métricas de rendimiento

### **Dashboard de Métricas**

```javascript
// Acceder a métricas de la PWA
if (window.divisaPWA) {
    console.log('App Version:', window.divisaPWA.getAppVersion());
    console.log('Cache Version:', window.divisaPWA.getCacheVersion());
    console.log('Is Standalone:', window.divisaPWA.isStandalone());
}
```

## 🚀 Futuras Implementaciones

### **Roadmap PWA**

- [ ] Notificaciones push en tiempo real
- [ ] Sincronización con calendario
- [ ] Widgets de escritorio
- [ ] Integración con apps nativas
- [ ] Modo offline avanzado
- [ ] Analytics avanzados

### **API de Notificaciones**

```javascript
// Solicitar permisos de notificación
if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('Notificaciones habilitadas');
        }
    });
}
```

## 📚 Recursos Adicionales

### **Documentación Oficial**

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web.dev PWA](https://web.dev/progressive-web-apps/)
- [Chrome PWA](https://developers.google.com/web/progressive-web-apps)

### **Herramientas de Desarrollo**

- [PWA Builder](https://www.pwabuilder.com/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Workbox](https://developers.google.com/web/tools/workbox)

## 🤝 Contribución

Para contribuir a la funcionalidad PWA:

1. Fork del repositorio
2. Crear rama para feature: `git checkout -b feature/pwa-enhancement`
3. Commit cambios: `git commit -am 'Add PWA feature'`
4. Push a la rama: `git push origin feature/pwa-enhancement`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---

**🎉 ¡DivisaAPI ahora es una PWA completa y moderna!**

Para soporte técnico o preguntas sobre la funcionalidad PWA, consulta la documentación o crea un issue en el repositorio. 