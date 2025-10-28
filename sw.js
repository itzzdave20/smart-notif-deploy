// Enhanced Service Worker with Offline/Online Sync
// This enables full offline functionality with automatic sync when online

const CACHE_NAME = 'chat-ping-v2.0.0';
const OFFLINE_CACHE = 'chat-ping-offline-v1';
const SYNC_QUEUE = 'sync-queue';

// Cache strategies for different types of requests
const CACHE_STRATEGIES = {
  // Static assets - cache first
  static: ['/static/', '/icons/', '/manifest.json'],
  // API calls - network first, cache fallback
  api: ['/api/', '/attendance/', '/notifications/'],
  // Pages - network first, cache fallback
  pages: ['/', '/dashboard', '/attendance', '/notifications']
};

// URLs to cache for offline use
const urlsToCache = [
  '/',
  '/manifest.json',
  '/sw.js',
  '/static/css/main.css',
  '/static/js/main.js',
  // Add more static assets as needed
];

// Install event - set up offline cache
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing offline-capable version...');
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(urlsToCache);
      }),
      // Set up offline database
      setupOfflineDatabase()
    ])
  );
});

// Activate event - clean up and set up sync
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating offline features...');
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Set up background sync
      setupBackgroundSync(),
      // Claim all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - handle online/offline requests
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests for offline handling
  if (request.method !== 'GET') {
    event.respondWith(handleNonGetRequest(request));
    return;
  }
  
  // Determine cache strategy based on URL
  const strategy = getCacheStrategy(url.pathname);
  
  switch (strategy) {
    case 'cache-first':
      event.respondWith(cacheFirst(request));
      break;
    case 'network-first':
      event.respondWith(networkFirst(request));
      break;
    case 'offline-only':
      event.respondWith(offlineOnly(request));
      break;
    default:
      event.respondWith(networkFirst(request));
  }
});

// Background sync for offline data
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered -', event.tag);
  
  switch (event.tag) {
    case 'attendance-sync':
      event.waitUntil(syncAttendanceData());
      break;
    case 'notification-sync':
      event.waitUntil(syncNotifications());
      break;
    case 'user-data-sync':
      event.waitUntil(syncUserData());
      break;
    case 'general-sync':
      event.waitUntil(syncAllOfflineData());
      break;
  }
});

// Push notifications with offline support
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  let notificationData = {
    title: 'Chat Ping Notification',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    data: {
      url: '/notifications',
      timestamp: Date.now()
    }
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = { ...notificationData, ...data };
    } catch (e) {
      notificationData.body = event.data.text();
    }
  }
  
  // Store notification for offline viewing
  storeOfflineNotification(notificationData);
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked');
  event.notification.close();
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      // Check if app is already open
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.focus();
          client.navigate(url);
          return;
        }
      }
      // Open new window if app is not open
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

// Cache strategies
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Offline - Content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/offline.html') || new Response(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Offline - Chat Ping</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .offline-icon { font-size: 64px; margin-bottom: 20px; }
            .retry-btn { background: #FF6B6B; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; }
          </style>
        </head>
        <body>
          <div class="offline-icon">📱</div>
          <h1>You're Offline</h1>
          <p>Some features are still available offline. Your data will sync when you're back online.</p>
          <button class="retry-btn" onclick="window.location.reload()">Retry</button>
        </body>
        </html>
      `, {
        headers: { 'Content-Type': 'text/html' }
      });
    }
    
    throw error;
  }
}

async function offlineOnly(request) {
  const cachedResponse = await caches.match(request);
  return cachedResponse || new Response('Offline only content', { status: 503 });
}

// Handle non-GET requests (POST, PUT, DELETE)
async function handleNonGetRequest(request) {
  try {
    // Try to make the request online
    const response = await fetch(request);
    return response;
  } catch (error) {
    // Store request for later sync if offline
    await storeOfflineRequest(request);
    
    // Return success response to user (data will sync later)
    return new Response(JSON.stringify({
      success: true,
      offline: true,
      message: 'Request queued for sync when online'
    }), {
      status: 202,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Offline data management
async function setupOfflineDatabase() {
  // This would set up IndexedDB for offline storage
  console.log('Service Worker: Setting up offline database');
}

async function storeOfflineRequest(request) {
  const requestData = {
    url: request.url,
    method: request.method,
    headers: Object.fromEntries(request.headers.entries()),
    body: await request.text(),
    timestamp: Date.now()
  };
  
  // Store in IndexedDB or cache
  const cache = await caches.open(OFFLINE_CACHE);
  await cache.put(`offline-request-${Date.now()}`, new Response(JSON.stringify(requestData)));
}

async function storeOfflineNotification(notification) {
  const cache = await caches.open(OFFLINE_CACHE);
  await cache.put(`notification-${Date.now()}`, new Response(JSON.stringify(notification)));
}

// Sync functions
async function syncAttendanceData() {
  console.log('Service Worker: Syncing attendance data...');
  try {
    const cache = await caches.open(OFFLINE_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('attendance')) {
        const response = await cache.match(request);
        const data = await response.json();
        
        // Send to server
        const syncResponse = await fetch('/api/attendance/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (syncResponse.ok) {
          await cache.delete(request);
        }
      }
    }
  } catch (error) {
    console.log('Service Worker: Attendance sync failed', error);
  }
}

async function syncNotifications() {
  console.log('Service Worker: Syncing notifications...');
  try {
    const cache = await caches.open(OFFLINE_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('notification')) {
        const response = await cache.match(request);
        const data = await response.json();
        
        // Send to server
        const syncResponse = await fetch('/api/notifications/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (syncResponse.ok) {
          await cache.delete(request);
        }
      }
    }
  } catch (error) {
    console.log('Service Worker: Notification sync failed', error);
  }
}

async function syncUserData() {
  console.log('Service Worker: Syncing user data...');
  // Implement user data sync
}

async function syncAllOfflineData() {
  console.log('Service Worker: Syncing all offline data...');
  await Promise.all([
    syncAttendanceData(),
    syncNotifications(),
    syncUserData()
  ]);
}

// Helper functions
function getCacheStrategy(pathname) {
  if (SYNC_STRATEGIES.static.some(pattern => pathname.includes(pattern))) {
    return 'cache-first';
  }
  if (SYNC_STRATEGIES.api.some(pattern => pathname.includes(pattern))) {
    return 'network-first';
  }
  return 'network-first';
}

async function setupBackgroundSync() {
  // Register background sync for different data types
  if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    try {
      await self.registration.sync.register('attendance-sync');
      await self.registration.sync.register('notification-sync');
      await self.registration.sync.register('user-data-sync');
    } catch (error) {
      console.log('Service Worker: Background sync registration failed', error);
    }
  }
}

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'SYNC_NOW') {
    syncAllOfflineData();
  }
  
  if (event.data && event.data.type === 'CACHE_DATA') {
    cacheOfflineData(event.data.data);
  }
});

async function cacheOfflineData(data) {
  const cache = await caches.open(OFFLINE_CACHE);
  await cache.put(`data-${Date.now()}`, new Response(JSON.stringify(data)));
}

console.log('Service Worker: Offline-capable version loaded successfully');