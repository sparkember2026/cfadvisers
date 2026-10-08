// Offline support: the app shell is cached; the data is fetched fresh when online and the cached copy
// is used offline. Bump VERSION when the shell changes.
const VERSION = "cfa-v1";
const SHELL = ["./", "index.html", "app.js", "app.css", "icon.svg", "manifest.webmanifest"];
self.addEventListener("install", (e) => e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener("activate", (e) => e.waitUntil(caches.keys().then((ks) =>
  Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin || url.pathname.includes("/v1/")) return;
  // network first, cache as fallback, for everything we serve (data changes; the shell is small)
  e.respondWith(fetch(e.request).then((res) => {
    if (res.ok) { const copy = res.clone(); caches.open(VERSION).then((c) => c.put(e.request, copy)); }
    return res;
  }).catch(() => caches.match(e.request).then((m) => m || caches.match("index.html"))));
});
