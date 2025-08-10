#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración del sistema
"""

from config import get_config, DatabaseConfig
import os

def test_configuration():
    """Prueba la configuración del sistema"""
    print("=== PRUEBA DE CONFIGURACIÓN ===\n")
    
    try:
        # 1. Probar configuración general
        print("1. Configuración General:")
        config = get_config()
        print(f"   - Entorno: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"   - Debug: {config.DEBUG}")
        print(f"   - Log Level: {config.LOG_LEVEL}")
        print(f"   - Rate Limit: {config.RATE_LIMIT_SECONDS} segundos")
        print(f"   - Update Interval: {config.UPDATE_INTERVAL_MINUTES} minutos")
        print(f"   - Request Timeout: {config.REQUEST_TIMEOUT} segundos")
        print()
        
        # 2. Probar configuración de base de datos
        print("2. Configuración de Base de Datos:")
        db_type = os.environ.get('DB_TYPE', 'sqlite')
        print(f"   - Tipo de BD: {db_type}")
        
        db_config = DatabaseConfig.get_database_config()
        print(f"   - URI: {db_config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   - Pool Size: {db_config['SQLALCHEMY_ENGINE_OPTIONS'].get('pool_size', 'N/A')}")
        print(f"   - Max Overflow: {db_config['SQLALCHEMY_ENGINE_OPTIONS'].get('max_overflow', 'N/A')}")
        print()
        
        # 3. Probar variables de entorno
        print("3. Variables de Entorno:")
        env_vars = [
            'DB_TYPE', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER',
            'FLASK_ENV', 'FLASK_DEBUG', 'LOG_LEVEL', 'RATE_LIMIT_SECONDS'
        ]
        
        for var in env_vars:
            value = os.environ.get(var, 'No definida')
            print(f"   - {var}: {value}")
        print()
        
        # 4. Probar configuración específica por tipo
        print("4. Configuraciones Específicas:")
        for db_type in ['postgresql', 'mariadb', 'sqlite']:
            try:
                specific_config = DatabaseConfig.get_database_config(db_type)
                print(f"   - {db_type.upper()}: {specific_config['SQLALCHEMY_DATABASE_URI']}")
            except Exception as e:
                print(f"   - {db_type.upper()}: Error - {str(e)}")
        print()
        
        print("✅ Configuración probada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la configuración: {str(e)}")
        return False

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("=== PRUEBA DE CONEXIÓN A BD ===\n")
    
    try:
        from models import db
        from flask import Flask
        
        # Crear app temporal para probar conexión
        app = Flask(__name__)
        db_config = DatabaseConfig.get_database_config()
        app.config.update(db_config)
        
        db.init_app(app)
        
        with app.app_context():
            # Intentar conectar
            db.engine.connect()
            print("✅ Conexión a la base de datos exitosa!")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        print("   Verifica que:")
        print("   - La base de datos esté ejecutándose")
        print("   - Las credenciales sean correctas")
        print("   - La red sea accesible")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de configuración...\n")
    
    # Probar configuración
    config_ok = test_configuration()
    
    if config_ok:
        print("\n" + "="*50 + "\n")
        # Probar conexión a BD
        test_database_connection()
    
    print("\n" + "="*50)
    print("Pruebas completadas.") 