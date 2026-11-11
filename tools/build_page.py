"""Embed data/data.json into src/template.html.

Writes index.html at the repo root (the GitHub Pages site, with offline support) and dist/artifact.html
(the same page without the offline parts, for publishing as a Claude artifact).
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PWA_HEAD = """<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#172024">
<link rel="icon" href="icons/icon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Kitchen">"""
PWA_JS = """if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
  window.addEventListener("load", () => { navigator.serviceWorker.register("sw.js").catch(() => {}); });
}
(function () {
  const net = document.createElement("span");
  const show = () => { net.textContent = navigator.onLine ? "" : "Offline: everything works except ordering links"; };
  document.querySelector(".facts").appendChild(net);
  window.addEventListener("online", show); window.addEventListener("offline", show); show();
})();"""

d = json.load(open(ROOT / "data" / "data.json", encoding="utf-8"))
s = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
t = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
assert t.count("/*DATA*/") == 1 and t.count("<!--PWA-->") == 1 and t.count("/*PWA_JS*/") == 1
core = (ROOT / "src" / "core.js").read_text(encoding="utf-8")
core += '\n' + (ROOT / 'src' / 'household.js').read_text(encoding='utf-8')
assert t.count("/*CORE_JS*/") == 1
page = t.replace("/*DATA*/", s).replace("/*CORE_JS*/", core).replace("/*HOUSEHOLD_UI*/", (ROOT / "src/household-ui.js").read_text(encoding="utf-8"))
site = page.replace("<!--PWA-->", PWA_HEAD).replace("/*PWA_JS*/", PWA_JS)
art = page.replace("<!--PWA-->\n", "").replace("\n/*PWA_JS*/", "")
(ROOT / "index.html").write_text(site, encoding="utf-8", newline="\n")
(ROOT / "dist").mkdir(exist_ok=True)
(ROOT / "dist" / "artifact.html").write_text(art, encoding="utf-8", newline="\n")
# a new cache name whenever the page changes, so phones drop the old copy
sw = ROOT / "sw.js"
build = hashlib.sha1(site.encode() + (ROOT / "manifest.webmanifest").read_text(encoding="utf-8").encode("utf-8")).hexdigest()[:10]
sw.write_text(re.sub(r'const VERSION = "kfz-[^"]*";', f'const VERSION = "kfz-{build}";', sw.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
print("index.html", len(site) // 1024, "KB; dist/artifact.html", len(art) // 1024, "KB; cache", build)
