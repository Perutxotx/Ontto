/* Service worker de Ontto.
 *
 * Ontto se usa en el monte, que es justo donde no hay cobertura. Así que todo
 * lo necesario para funcionar tiene que estar ya en el teléfono.
 *
 * Tres políticas, y la del medio es la que faltaba:
 *   - El mapa (base.json, ~900 KB, cambia una vez al año)  -> caché primero
 *   - La carcasa (index.html, sw.js, manifest)             -> red primero
 *   - El índice diario (disparo.json)                      -> red primero
 *
 * Por qué la carcasa cambió a red primero: con caché primero y una VERSION
 * fija, el index.html que se guardó el día de la instalación se servía para
 * siempre. Cualquier arreglo posterior no llegaba nunca al móvil ya instalado.
 * Es HTML de 30 KB; pedirlo a la red cuando la hay no cuesta nada, y sin red
 * sigue saliendo el de la caché.
 */
const VERSION = 'ontto-v2';
const ESENCIAL = [
  './',
  './index.html',
  './manifest.json',
  './datos/base.json',
  './datos/disparo.json',
  './iconos/icono-192.png',
  './iconos/icono-512.png'
];

// La carcasa: lo que debe poder corregirse solo.
function esCarcasa(url) {
  return url.pathname.endsWith('/index.html')
      || url.pathname.endsWith('/manifest.json')
      || url.pathname.endsWith('/')
      || url.pathname.endsWith('/datos/disparo.json');
}

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

self.addEventListener('message', function (e) {
  if (e.data === 'saltar') self.skipWaiting();
});

self.addEventListener('fetch', function (e) {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;      // tipografías: que las lleve el navegador

  // Red primero, caché de respaldo. Solo se guarda lo que viene bien: una
  // respuesta 404 o 500 en caché es peor que no tener nada.
  if (esCarcasa(url)) {
    e.respondWith(
      fetch(req).then(function (r) {
        if (r && r.ok) {
          const copia = r.clone();
          caches.open(VERSION).then(function (c) { c.put(req, copia); });
        }
        return r;
      }).catch(function () {
        return caches.match(req).then(function (hit) {
          return hit || caches.match('./index.html');
        });
      })
    );
    return;
  }

  // Todo lo demás (el mapa, los iconos): caché primero.
  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (r) {
        if (r && r.ok) {
          const copia = r.clone();
          caches.open(VERSION).then(function (c) { c.put(req, copia); });
        }
        return r;
      }).catch(function () {
        if (req.mode === 'navigate') return caches.match('./index.html');
        return new Response('', {status: 504, statusText: 'sin conexión'});
      });
    })
  );
});
