const CACHE = "cyl-v1";
const FILES = [
  "/cylinder-monitor/",
  "/cylinder-monitor/index.html",
  "/cylinder-monitor/manifest.json",
  "/cylinder-monitor/icon.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)));
});

self.addEventListener("fetch", e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
