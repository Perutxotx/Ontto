/* Service worker de Ontto.
 *
 * Ontto se usa en el monte, que es justo donde no hay cobertura. Así que todo
 * lo necesario para funcionar tiene que estar ya en el teléfono.
 *
 * Dos políticas:
 *   - El mapa y la carcasa cambian una vez al año  -> caché primero
 *   - El índice diario cambia cada mañana          -> red primero, caché de respaldo
 */
const VERSION = 'ontto-v1';
const ESENCIAL = [
  './',
  './index.html',
  './manifest.json',
  './datos/base.json',
  './datos/disparo.json',
  './iconos/icono-192.png',
  './iconos/icono-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(VERSION)
      .then(function (c) { return c.addAll(ESENCIAL); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (ks) {
        return Promise.all(ks.filter(function (k) { return k !== VERSION; })
                            .map(function (k) { return caches.delete(k); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // El índice del día: intentar red, y si no hay, servir lo último que tengamos.
  if (url.pathname.endsWith('/datos/disparo.json')) {
    e.respondWith(
      fetch(req).then(function (r) {
        const copia = r.clone();
        caches.open(VERSION).then(function (c) { c.put(req, copia); });
        return r;
      }).catch(function () {
        return caches.match(req);
      })
    );
    return;
  }

  // Todo lo demás: caché primero. Si no está, red, y se guarda.
  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (r) {
        if (r && r.status === 200 && (url.origin === location.origin
            || url.host === 'fonts.gstatic.com' || url.host === 'fonts.googleapis.com')) {
          const copia = r.clone();
          caches.open(VERSION).then(function (c) { c.put(req, copia); });
        }
        return r;
      }).catch(function () {
        // sin red y sin caché: al menos devolver la portada para no romper la navegación
        if (req.mode === 'navigate') return caches.match('./index.html');
        return new Response('', {status: 504, statusText: 'sin conexión'});
      });
    })
  );
});
