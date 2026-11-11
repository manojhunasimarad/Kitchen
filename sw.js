/* Offline support for Kitchen From Zero on GitHub Pages.
   The app is one HTML file, so caching it (plus the icons and fonts) makes the whole app work offline.
   Pages: network first, falling back to the cache, so you get updates when online and the last copy offline.
   Icons and fonts: cache first. */
const VERSION = "kfz-145eb514e1";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png",
  "./icons/maskable-512.png", "./icons/icon-180.png", "./icons/icon-32.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith("kfz-") && k !== VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const isPage = req.mode === "navigate" || (url.origin === location.origin && /\/(index\.html)?$/.test(url.pathname));
  if (isPage) {
    e.respondWith(fetch(req).then(res => {
      if (!res.ok) throw new Error("Page fetch failed");
      const copy = res.clone();
      caches.open(VERSION).then(c => c.put("./index.html", copy));
      return res;
    }).catch(() => caches.match("./index.html").then(r => r || caches.match("./"))));
    return;
  }
  const cacheable = url.origin === location.origin || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!cacheable) return;  // grocery-app links and anything else go straight to the network
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res && (res.ok || res.type === "opaque")) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
    return res;
  })));
});
