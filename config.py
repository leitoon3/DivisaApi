import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Config:
    """Clase base de configuración"""
    
    # Configuración general de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_for_dev')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuración de rate limiting
    RATE_LIMIT_SECONDS = int(os.environ.get('RATE_LIMIT_SECONDS', '10'))
    
    # Configuración de actualización automática
    UPDATE_INTERVAL_MINUTES = int(os.environ.get('UPDATE_INTERVAL_MINUTES', '30'))
    
    # Configuración de timeout para requests
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
    
    # Configuración de pool de conexiones
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '10'))
    DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', '20'))
    DB_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '300'))
    DB_POOL_PRE_PING = os.environ.get('DB_POOL_PRE_PING', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'

# Configuraciones específicas por base de datos
class DatabaseConfig:
    """Configuraciones para diferentes bases de datos"""
    
    @staticmethod
    def get_postgresql_config() -> Dict[str, Any]:
        """
        Configuración para PostgreSQL
        
        Variables de entorno requeridas:
        - DB_HOST: Host de la base de datos
        - DB_PORT: Puerto de la base de datos
        - DB_NAME: Nombre de la base de datos
        - DB_USER: Usuario de la base de datos
        - DB_PASSWORD: Contraseña de la base de datos
        
        Ejemplo de uso:
        export DB_HOST=localhost
        export DB_PORT=5432
        export DB_NAME=divisa_api
        export DB_USER=postgres
        export DB_PASSWORD=mi_password
        """
        return {
            'SQLALCHEMY_DATABASE_URI': (
                f"postgresql://{os.environ.get('DB_USER', 'postgres')}:"
                f"{os.environ.get('DB_PASSWORD', '')}@"
                f"{os.environ.get('DB_HOST', 'localhost')}:"
                f"{os.environ.get('DB_PORT', '5432')}/"
                f"{os.environ.get('DB_NAME', 'divisa_api')}"
            ),
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '300')),
                'pool_pre_ping': os.environ.get('DB_POOL_PRE_PING', 'True').lower() == 'true'
            }
        }
    
    @staticmethod
    def get_mariadb_config() -> Dict[str, Any]:
        """
        Configuración para MariaDB/MySQL
        
        Variables de entorno requeridas:
        - DB_HOST: Host de la base de datos
        - DB_PORT: Puerto de la base de datos
        - DB_NAME: Nombre de la base de datos
        - DB_USER: Usuario de la base de datos
        - DB_PASSWORD: Contraseña de la base de datos
        
        Ejemplo de uso:
        export DB_HOST=localhost
        export DB_PORT=3306
        export DB_NAME=divisa_api
        export DB_USER=root
        export DB_PASSWORD=mi_password
        """
        return {
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:"
                f"{os.environ.get('DB_PASSWORD', '')}@"
                f"{os.environ.get('DB_HOST', 'localhost')}:"
                f"{os.environ.get('DB_PORT', '3306')}/"
                f"{os.environ.get('DB_NAME', 'divisa_api')}"
                "?charset=utf8mb4"
            ),
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '300')),
                'pool_pre_ping': os.environ.get('DB_POOL_PRE_PING', 'True').lower() == 'true'
            }
        }
    
    @staticmethod
    def get_sqlite_config() -> Dict[str, Any]:
        """
        Configuración para SQLite (desarrollo local)
        
        Variables de entorno opcionales:
        - DB_PATH: Ruta al archivo de base de datos
        
        Ejemplo de uso:
        export DB_PATH=./divisa_api.db
        """
        db_path = os.environ.get('DB_PATH', './divisa_api.db')
        return {
            'SQLALCHEMY_DATABASE_URI': f"sqlite:///{db_path}",
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True
            }
        }
    
    @staticmethod
    def get_database_config(database_type: str = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de base de datos según el tipo especificado
        
        Args:
            database_type: Tipo de base de datos ('postgresql', 'mariadb', 'sqlite')
                          Si no se especifica, se determina por variable de entorno DB_TYPE
        
        Returns:
            Dict con la configuración de la base de datos
        """
        if not database_type:
            database_type = os.environ.get('DB_TYPE', 'sqlite').lower()
        
        if database_type == 'postgresql':
            return DatabaseConfig.get_postgresql_config()
        elif database_type == 'mariadb':
            return DatabaseConfig.get_mariadb_config()
        elif database_type == 'sqlite':
            return DatabaseConfig.get_sqlite_config()
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {database_type}")

# Configuraciones por entorno
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env_name: str = None) -> Config:
    """
    Obtiene la configuración según el entorno especificado
    
    Args:
        env_name: Nombre del entorno ('development', 'production', 'testing')
                 Si no se especifica, se determina por variable de entorno FLASK_ENV
    
    Returns:
        Instancia de la clase de configuración
    """
    if not env_name:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_by_name.get(env_name, config_by_name['default'])
    return config_class()

# Ejemplos de uso y configuración
if __name__ == "__main__":
    print("=== Ejemplos de Configuración ===\n")
    
    print("1. Configuración para PostgreSQL:")
    print("export DB_TYPE=postgresql")
    print("export DB_HOST=localhost")
    print("export DB_PORT=5432")
    print("export DB_NAME=divisa_api")
    print("export DB_USER=postgres")
    print("export DB_PASSWORD=mi_password\n")
    
    print("2. Configuración para MariaDB:")
    print("export DB_TYPE=mariadb")
    print("export DB_HOST=localhost")
    print("export DB_PORT=3306")
    print("export DB_NAME=divisa_api")
    print("export DB_USER=root")
    print("export DB_PASSWORD=mi_password\n")
    
    print("3. Configuración para SQLite:")
    print("export DB_TYPE=sqlite")
    print("export DB_PATH=./divisa_api.db\n")
    
    print("4. Configuración del entorno:")
    print("export FLASK_ENV=development")
    print("export FLASK_DEBUG=true")
    print("export LOG_LEVEL=DEBUG\n")
    
    print("5. Configuración de rate limiting:")
    print("export RATE_LIMIT_SECONDS=15")
    print("export UPDATE_INTERVAL_MINUTES=60\n")
    
    print("6. Configuración de pool de conexiones:")
    print("export DB_POOL_SIZE=20")
    print("export DB_MAX_OVERFLOW=30")
    print("export DB_POOL_RECYCLE=600") 