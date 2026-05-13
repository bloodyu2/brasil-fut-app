const CACHE_NAME = 'brasil-fut-v2';
const assets = [
  './brasil-fut.html',
  './assets/favicon-32.png',
  './assets/favicon-16.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(assets))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
