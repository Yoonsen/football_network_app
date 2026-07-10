const CACHE_NAME = 'football-network-v1';
const ASSETS_TO_CACHE = [
  '/index.html',
  '/style.css',
  '/app.js',
  '/graph_2022.json',
  '/graph_2026.json',
  'https://unpkg.com/vis-network/standalone/umd/vis-network.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
