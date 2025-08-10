#!/usr/bin/env python3
"""
Configuración de PWA para DivisaAPI
Configuraciones específicas para Progressive Web App
"""

import os
from datetime import datetime

class PWAConfig:
    """Configuración de la PWA DivisaAPI"""
    
    # Información básica de la aplicación
    APP_NAME = "DivisaAPI - Tipos de Cambio BCV"
    APP_SHORT_NAME = "DivisaAPI"
    APP_DESCRIPTION = "API moderna para tipos de cambio del Banco Central de Venezuela con interfaz web integrada"
    APP_VERSION = "1.1.0"
    
    # Configuración del manifest
    MANIFEST_CONFIG = {
        "name": APP_NAME,
        "short_name": APP_SHORT_NAME,
        "description": APP_DESCRIPTION,
        "version": APP_VERSION,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#6366f1",
        "orientation": "portrait-primary",
        "scope": "/",
        "lang": "es",
        "categories": ["finance", "business", "utilities"]
    }
    
    # Configuración del Service Worker
    SW_CONFIG = {
        "cache_name": f"divisa-api-{APP_VERSION}",
        "static_cache": f"divisa-static-{APP_VERSION}",
        "dynamic_cache": f"divisa-dynamic-{APP_VERSION}",
        "update_interval": 30,  # minutos
        "cache_expiry": 24 * 60 * 60 * 1000,  # 24 horas en ms
        "max_cache_size": 50 * 1024 * 1024  # 50MB
    }
    
    # Rutas de la API para cache
    API_ROUTES = [
        "/api/rates",
        "/api/status", 
        "/api/health",
        "/api/convert",
        "/api/history"
    ]
    
    # Archivos estáticos para cache offline
    STATIC_FILES = [
        "/",
        "/static/manifest.json",
        "/static/icons/icon-192x192.png",
        "/static/icons/icon-512x512.png",
        "/static/css/app.css",
        "/static/js/app.js",
        "/templates/index.html"
    ]
    
    # Configuración de notificaciones push
    PUSH_CONFIG = {
        "enabled": True,
        "vapid_public_key": os.getenv("VAPID_PUBLIC_KEY", ""),
        "vapid_private_key": os.getenv("VAPID_PRIVATE_KEY", ""),
        "notification_title": "DivisaAPI",
        "notification_body": "Nuevos tipos de cambio disponibles",
        "notification_icon": "/static/icons/icon-192x192.png"
    }
    
    # Configuración de sincronización en background
    BACKGROUND_SYNC_CONFIG = {
        "enabled": True,
        "sync_tags": ["update-rates", "sync-data"],
        "retry_attempts": 3,
        "retry_delay": 5000  # 5 segundos
    }
    
    # Configuración de instalación
    INSTALL_CONFIG = {
        "show_prompt": True,
        "prompt_delay": 5000,  # 5 segundos
        "auto_install": False,
        "install_button_position": "bottom-right"
    }
    
    # Configuración de métricas y analytics
    METRICS_CONFIG = {
        "enabled": True,
        "track_installations": True,
        "track_usage": True,
        "track_performance": True
    }
    
    @classmethod
    def get_manifest_json(cls):
        """Generar el contenido del manifest.json"""
        import json
        
        manifest = cls.MANIFEST_CONFIG.copy()
        
        # Agregar iconos
        manifest["icons"] = [
            {
                "src": "/static/icons/icon-72x72.png",
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-128x128.png",
                "sizes": "128x128",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-144x144.png",
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-152x152.png",
                "sizes": "152x152",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-384x384.png",
                "sizes": "384x384",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable any"
            }
        ]
        
        # Agregar shortcuts
        manifest["shortcuts"] = [
            {
                "name": "Ver Tasas",
                "short_name": "Tasas",
                "description": "Ver todos los tipos de cambio",
                "url": "/?section=rates",
                "icons": [
                    {
                        "src": "/static/icons/icon-96x96.png",
                        "sizes": "96x96"
                    }
                ]
            },
            {
                "name": "Convertir Divisas",
                "short_name": "Convertir",
                "description": "Convertir entre diferentes monedas",
                "url": "/?section=converter",
                "icons": [
                    {
                        "src": "/static/icons/icon-96x96.png",
                        "sizes": "96x96"
                    }
                ]
            }
        ]
        
        return json.dumps(manifest, indent=2, ensure_ascii=False)
    
    @classmethod
    def get_pwa_info(cls):
        """Obtener información de la PWA"""
        return {
            "name": cls.APP_NAME,
            "version": cls.APP_VERSION,
            "description": cls.APP_DESCRIPTION,
            "features": {
                "offline_support": True,
                "installable": True,
                "background_sync": cls.BACKGROUND_SYNC_CONFIG["enabled"],
                "push_notifications": cls.PUSH_CONFIG["enabled"],
                "cache_strategy": "Network First with Cache Fallback"
            },
            "cache_config": cls.SW_CONFIG,
            "api_routes": cls.API_ROUTES,
            "static_files": cls.STATIC_FILES,
            "last_updated": datetime.now().isoformat()
        }
    
    @classmethod
    def validate_config(cls):
        """Validar la configuración de la PWA"""
        errors = []
        warnings = []
        
        # Verificar archivos estáticos
        for file_path in cls.STATIC_FILES:
            if not file_path.startswith("/"):
                errors.append(f"Ruta de archivo estático debe comenzar con '/': {file_path}")
        
        # Verificar iconos
        icon_dir = "static/icons"
        if not os.path.exists(icon_dir):
            errors.append(f"Directorio de iconos no existe: {icon_dir}")
        else:
            required_icons = [
                "icon-72x72.png", "icon-96x96.png", "icon-128x128.png",
                "icon-144x144.png", "icon-152x152.png", "icon-192x192.png",
                "icon-384x384.png", "icon-512x512.png"
            ]
            
            for icon in required_icons:
                icon_path = os.path.join(icon_dir, icon)
                if not os.path.exists(icon_path):
                    errors.append(f"Icono requerido no encontrado: {icon}")
        
        # Verificar manifest
        manifest_path = "static/manifest.json"
        if not os.path.exists(manifest_path):
            errors.append(f"Manifest no encontrado: {manifest_path}")
        
        # Verificar Service Worker
        sw_path = "static/sw.js"
        if not os.path.exists(sw_path):
            errors.append(f"Service Worker no encontrado: {sw_path}")
        
        # Verificar CSS y JS
        css_path = "static/css/app.css"
        js_path = "static/js/app.js"
        
        if not os.path.exists(css_path):
            warnings.append(f"CSS de PWA no encontrado: {css_path}")
        
        if not os.path.exists(js_path):
            warnings.append(f"JavaScript de PWA no encontrado: {js_path}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Mostrar información de la PWA
    print("🚀 Configuración de PWA DivisaAPI")
    print("=" * 50)
    
    config = PWAConfig()
    print(f"📱 Nombre: {config.APP_NAME}")
    print(f"🔢 Versión: {config.APP_VERSION}")
    print(f"📝 Descripción: {config.APP_DESCRIPTION}")
    
    print("\n⚙️ Configuración del Service Worker:")
    for key, value in config.SW_CONFIG.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔗 Rutas de API para cache: {len(config.API_ROUTES)}")
    print(f"📁 Archivos estáticos: {len(config.STATIC_FILES)}")
    
    print("\n✅ Validando configuración...")
    validation = config.validate_config()
    
    if validation["valid"]:
        print("✅ Configuración válida")
    else:
        print("❌ Errores encontrados:")
        for error in validation["errors"]:
            print(f"   - {error}")
    
    if validation["warnings"]:
        print("⚠️ Advertencias:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")
    
    print(f"\n🕒 Última validación: {validation['timestamp']}") 