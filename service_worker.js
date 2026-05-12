const CACHE = "cyl-v7";
const FILES = [
  "/cylinder-monitor/",
  "/cylinder-monitor/index.html",
  "/cylinder-monitor/manifest.json",
  "/cylinder-monitor/processor.js",
  "/cylinder-monitor/detector.py",
  "/cylinder-monitor/icon.png"
];
self.addEventListener("install",  e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))); });
self.addEventListener("fetch",    e => { e.respondWith(caches.match(e.request).then(r => r || fetch(e.request))); });
