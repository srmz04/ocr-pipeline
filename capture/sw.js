// Service Worker for PWA - Caches app shell for offline use
const CACHE_NAME = 'captura-vacunas-v2';
const STATIC_ASSETS = [
    './',
    './index.html',
    './styles.css',
    './config.js',
    './camera.js',
    './validator.js',
    './uploader.js',
    './offline-manager.js',
    './app.js',
    './manifest.json',
    './icon.png'
];

// Install: Cache all static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching app shell');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate: Clean old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch: Cache-first for static assets, network-first for API calls
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET requests and API calls (proxy uploads)
    if (event.request.method !== 'GET' || url.hostname === 'script.google.com') {
        return; // Let the browser handle it normally
    }

    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(event.request).catch(() => {
                    // If offline and not cached, return a fallback for HTML
                    if (event.request.headers.get('accept').includes('text/html')) {
                        return caches.match('./index.html');
                    }
                });
            })
    );
});
