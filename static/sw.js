const CACHE_NAME = 'divisa-api-v1.1.0';
const STATIC_CACHE = 'divisa-static-v1.1.0';
const DYNAMIC_CACHE = 'divisa-dynamic-v1.1.0';

// Archivos estáticos para cache offline
const STATIC_FILES = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/css/app.css',
  '/static/js/app.js'
];

// Rutas de la API que queremos cachear
const API_ROUTES = [
  '/api/rates',
  '/api/status',
  '/api/health'
];

// Estrategia de cache: Cache First para archivos estáticos
async function cacheStaticFiles() {
  const cache = await caches.open(STATIC_CACHE);
  return cache.addAll(STATIC_FILES);
}

// Estrategia de cache: Network First para API, fallback a cache
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Estrategia de cache: Cache First para archivos estáticos
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    throw error;
  }
}

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker instalando...');
  event.waitUntil(
    cacheStaticFiles().then(() => {
      console.log('Archivos estáticos cacheados exitosamente');
      return self.skipWaiting();
    })
  );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker activando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('Eliminando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activado y cache limpiado');
      return self.clients.claim();
    })
  );
});

// Interceptar fetch requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Cache estático para archivos CSS, JS, imágenes y manifest
  if (request.destination === 'style' || 
      request.destination === 'script' || 
      request.destination === 'image' ||
      url.pathname === '/static/manifest.json') {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Network First para rutas de API
  if (API_ROUTES.some(route => url.pathname.startsWith(route))) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Cache First para la página principal
  if (url.pathname === '/' || url.pathname === '/index.html') {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Para otras rutas, usar Network First
  event.respondWith(networkFirst(request));
});

// Manejar mensajes del cliente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// Sincronización en background para actualizar tipos de cambio
self.addEventListener('sync', (event) => {
  if (event.tag === 'update-rates') {
    console.log('Sincronización en background: actualizando tipos de cambio');
    event.waitUntil(updateRatesInBackground());
  }
});

// Función para actualizar tipos de cambio en background
async function updateRatesInBackground() {
  try {
    const response = await fetch('/api/update', { method: 'POST' });
    if (response.ok) {
      console.log('Tipos de cambio actualizados en background');
      
      // Notificar a todos los clientes
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'RATES_UPDATED',
          timestamp: new Date().toISOString()
        });
      });
    }
  } catch (error) {
    console.error('Error actualizando tipos de cambio en background:', error);
  }
}

// Manejar push notifications (para futuras implementaciones)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body || 'Nuevos tipos de cambio disponibles',
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      },
      actions: [
        {
          action: 'explore',
          title: 'Ver Tasas',
          icon: '/static/icons/icon-96x96.png'
        },
        {
          action: 'close',
          title: 'Cerrar',
          icon: '/static/icons/icon-96x96.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'DivisaAPI', options)
    );
  }
});

// Manejar clicks en notificaciones
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/?section=rates')
    );
  }
}); 