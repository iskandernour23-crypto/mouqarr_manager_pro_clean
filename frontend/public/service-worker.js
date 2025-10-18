const CACHE_NAME = 'mouqarr-shell-v1';
const OFFLINE_URLS = [
  '/',
  '/index.html',
  '/manifest.webmanifest'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
});

const queueKey = 'mouqarr-offline-queue';

const persistRequest = async (request, body) => {
  const queue = await caches.open(queueKey);
  const requests = (await queue.match('queue')) ? await (await queue.match('queue')).json() : [];
  requests.push({
    url: request.url,
    method: request.method,
    body,
    headers: [...request.headers.entries()]
  });
  await queue.put('queue', new Response(JSON.stringify(requests)));
};

const flushQueue = async () => {
  const queue = await caches.open(queueKey);
  const stored = await queue.match('queue');
  if (!stored) return;
  const requests = await stored.json();
  await queue.delete('queue');
  for (const item of requests) {
    try {
      await fetch(item.url, {
        method: item.method,
        headers: new Headers(item.headers),
        body: item.body
      });
    } catch (error) {
      console.error('Retry failed', error);
    }
  }
};

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method === 'GET') {
    event.respondWith(
      caches.match(request).then((cached) =>
        cached || fetch(request).then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return response;
        }).catch(() => caches.match('/index.html'))
      )
    );
  } else if (!navigator.onLine) {
    event.respondWith(
      (async () => {
        const body = await request.clone().text();
        await persistRequest(request, body);
        return new Response(
          JSON.stringify({ status: 'queued', offline: true }),
          { headers: { 'Content-Type': 'application/json' } }
        );
      })()
    );
  }
});

self.addEventListener('sync', (event) => {
  if (event.tag === 'flush-offline') {
    event.waitUntil(flushQueue());
  }
});

self.addEventListener('message', (event) => {
  if (event.data === 'flush-queue') {
    event.waitUntil(flushQueue());
  }
});
