// Service worker: mette in cache SOLO la "shell" dell'app (stesso dominio).
// Le richieste verso YouTube/googleapis/ytimg NON vengono intercettate.
// Strategia: rete prima (cosi' gli aggiornamenti arrivano subito), cache se offline.
// Per forzare la pulizia delle vecchie cache: incrementa CACHE_VERSION.
const CACHE_VERSION = 'ytc-v1.1.1';
const SHELL = [
  './',
  'index.html',
  'manifest.webmanifest',
  'css/style.css',
  'js/main.js',
  'js/util.js',
  'js/keymap.js',
  'js/settings.js',
  'js/controller-info.js',
  'js/favorites.js',
  'js/search.js',
  'js/player.js',
  'js/fullscreen.js',
  'js/controls.js',
  'icons/icon.svg',
  'icons/apple-touch-icon.png',
  'icons/apple-touch-icon-152.png',
  'icons/apple-touch-icon-167.png',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-maskable-512.png',
  'icons/favicon-32.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('ytc-') && k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  // solo GET dello stesso dominio e dentro lo scope dell'app; tutto il resto passa diretto
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  if (!url.pathname.startsWith(new URL(self.registration.scope).pathname)) return;
  if (url.pathname.includes('/test/')) return; // pagina di prova fase 0: non toccarla

  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req, { ignoreSearch: true }).then((r) => r || (req.mode === 'navigate' ? caches.match('index.html') : Response.error())))
  );
});
