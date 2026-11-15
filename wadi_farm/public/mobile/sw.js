const CACHE = 'wf-mobile-v040';
const ASSETS = [
  '/assets/wadi_farm/mobile/index.html',
  '/assets/wadi_farm/mobile/style.css',
  '/assets/wadi_farm/mobile/app.js',
  '/assets/wadi_farm/mobile/manifest.json',
  '/assets/wadi_farm/logo.svg'
];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('wf-mobile-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const path = new URL(event.request.url).pathname;
  if (!path.startsWith('/assets/wadi_farm/mobile/') && path !== '/assets/wadi_farm/logo.svg') return;
  event.respondWith(caches.match(event.request).then(hit => hit || fetch(event.request)));
});
