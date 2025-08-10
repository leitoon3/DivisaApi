// DivisaAPI PWA - JavaScript Principal
class DivisaPWA {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.updateAvailable = false;
        this.serviceWorker = null;
        
        this.init();
    }
    
    async init() {
        console.log('Inicializando DivisaAPI PWA...');
        
        // Registrar Service Worker
        await this.registerServiceWorker();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Verificar estado de instalación
        this.checkInstallationStatus();
        
        // Configurar sincronización en background
        this.setupBackgroundSync();
        
        // Verificar actualizaciones
        this.checkForUpdates();
        
        console.log('DivisaAPI PWA inicializada correctamente');
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.serviceWorker = await navigator.serviceWorker.register('/static/sw.js');
                console.log('Service Worker registrado:', this.serviceWorker);
                
                // Escuchar mensajes del Service Worker
                navigator.serviceWorker.addEventListener('message', (event) => {
                    this.handleServiceWorkerMessage(event.data);
                });
                
                // Escuchar actualizaciones del Service Worker
                this.serviceWorker.addEventListener('updatefound', () => {
                    console.log('Nueva versión del Service Worker disponible');
                    this.updateAvailable = true;
                    this.showUpdateNotification();
                });
                
            } catch (error) {
                console.error('Error registrando Service Worker:', error);
            }
        } else {
            console.warn('Service Worker no soportado en este navegador');
        }
    }
    
    setupEventListeners() {
        // Evento de instalación de PWA
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt();
        });
        
        // Evento de instalación completada
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallPrompt();
            this.showSuccessMessage('¡DivisaAPI instalada exitosamente!');
            console.log('PWA instalada');
        });
        
        // Eventos de conectividad
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateOnlineStatus(true);
            this.syncData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateOnlineStatus(false);
        });
        
        // Eventos de visibilidad para sincronización
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.isOnline) {
                this.syncData();
            }
        });
        
        // Eventos de focus para verificar actualizaciones
        window.addEventListener('focus', () => {
            this.checkForUpdates();
        });
    }
    
    checkInstallationStatus() {
        // Verificar si la app está instalada
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            this.hideInstallPrompt();
        }
    }
    
    setupBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            // Registrar sincronización para actualización de tipos de cambio
            navigator.serviceWorker.ready.then((registration) => {
                registration.sync.register('update-rates');
            });
        }
    }
    
    async checkForUpdates() {
        if (this.serviceWorker && this.updateAvailable) {
            try {
                // Enviar mensaje al Service Worker para actualizar
                this.serviceWorker.postMessage({ type: 'SKIP_WAITING' });
                
                // Recargar la página para aplicar la nueva versión
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
                
            } catch (error) {
                console.error('Error aplicando actualización:', error);
            }
        }
    }
    
    showInstallPrompt() {
        // Crear banner de instalación
        if (!document.getElementById('pwa-install-banner')) {
            const banner = document.createElement('div');
            banner.id = 'pwa-install-banner';
            banner.className = 'pwa-install-banner';
            banner.innerHTML = `
                <div class="pwa-install-content">
                    <div class="pwa-install-info">
                        <i data-feather="download" class="pwa-install-icon"></i>
                        <div>
                            <h4>Instalar DivisaAPI</h4>
                            <p>Accede rápidamente a los tipos de cambio del BCV</p>
                        </div>
                    </div>
                    <div class="pwa-install-actions">
                        <button class="btn btn-primary btn-sm" onclick="divisaPWA.installApp()">
                            Instalar
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="divisaPWA.hideInstallPrompt()">
                            Más tarde
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(banner);
            
            // Inicializar iconos
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }
    
    hideInstallPrompt() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.remove();
        }
    }
    
    async installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                console.log('Usuario aceptó instalar la PWA');
            } else {
                console.log('Usuario rechazó instalar la PWA');
            }
            
            this.deferredPrompt = null;
            this.hideInstallPrompt();
        }
    }
    
    updateOnlineStatus(isOnline) {
        const statusElement = document.getElementById('online-status');
        if (statusElement) {
            statusElement.className = isOnline ? 'online' : 'offline';
            statusElement.textContent = isOnline ? 'En línea' : 'Sin conexión';
        }
        
        // Mostrar notificación de estado
        if (!isOnline) {
            this.showOfflineMessage();
        }
    }
    
    showOfflineMessage() {
        const message = document.createElement('div');
        message.className = 'offline-message';
        message.innerHTML = `
            <div class="offline-content">
                <i data-feather="wifi-off"></i>
                <span>Sin conexión - Usando datos cacheados</span>
            </div>
        `;
        
        document.body.appendChild(message);
        
        // Inicializar iconos
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Remover mensaje después de 5 segundos
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 5000);
    }
    
    async syncData() {
        if (this.isOnline && 'serviceWorker' in navigator) {
            try {
                // Sincronizar datos en background
                const registration = await navigator.serviceWorker.ready;
                if ('sync' in registration) {
                    await registration.sync.register('update-rates');
                    console.log('Sincronización en background registrada');
                }
            } catch (error) {
                console.error('Error en sincronización:', error);
            }
        }
    }
    
    handleServiceWorkerMessage(data) {
        switch (data.type) {
            case 'RATES_UPDATED':
                this.handleRatesUpdate(data.timestamp);
                break;
            default:
                console.log('Mensaje del Service Worker:', data);
        }
    }
    
    handleRatesUpdate(timestamp) {
        console.log('Tipos de cambio actualizados:', timestamp);
        
        // Mostrar notificación
        this.showSuccessMessage('Tipos de cambio actualizados');
        
        // Recargar datos si es necesario
        if (typeof loadExchangeRates === 'function') {
            loadExchangeRates();
        }
    }
    
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <i data-feather="refresh-cw"></i>
                <span>Nueva versión disponible</span>
                <button class="btn btn-primary btn-sm" onclick="divisaPWA.applyUpdate()">
                    Actualizar
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Inicializar iconos
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Remover notificación después de 10 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
    
    applyUpdate() {
        this.checkForUpdates();
    }
    
    showSuccessMessage(message) {
        // Crear toast de éxito
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <i data-feather="check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Inicializar iconos
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Mostrar toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Ocultar y remover toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // Métodos de utilidad
    isStandalone() {
        return window.matchMedia('(display-mode: standalone)').matches || 
               window.navigator.standalone === true;
    }
    
    getAppVersion() {
        return '1.1.0';
    }
    
    getCacheVersion() {
        return 'divisa-api-v1.1.0';
    }
}

// Inicializar PWA cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.divisaPWA = new DivisaPWA();
});

// Exportar para uso global
window.DivisaPWA = DivisaPWA; 