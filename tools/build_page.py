"""Embed data/data.json into src/template.html and write index.html at the repo root."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.load(open(ROOT / "data" / "data.json"))
s = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
t = (ROOT / "src" / "template.html").read_text()
assert t.count("/*DATA*/") == 1
(ROOT / "index.html").write_text(t.replace("/*DATA*/", s))
print("index.html", (ROOT / "index.html").stat().st_size // 1024, "KB")
