const CACHE_NAME = 'bmv3-cache-v3';
const ASSETS_TO_CACHE = [
  '/offline/',
  '/static/core/image/bmv3_logo.png',
  '/static/core/image/background_pic.png',
  '/static/core/image/bmv3_background.png'
];

// On install, cache shell assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Clean up old caches on activate
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Intercept requests
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Network First, fallback to cache strategy for HTML views/API calls
  if (event.request.mode === 'navigate' || url.pathname.startsWith('/api/') || url.pathname.includes('/parent/') || url.pathname.includes('/teacher/') || url.pathname.includes('/dashboard/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone the response and save it to cache if successful
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Offline fallback
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;
            // If page is HTML view, fallback to cached offline page
            if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline/');
            }
          });
        })
    );
  } else {
    // Cache First, fallback to network strategy for static assets
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) return cachedResponse;

        return fetch(event.request).then((response) => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        });
      })
    );
  }
});
