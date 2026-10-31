"""Extract the four master recipes of Book 1 (Restaurant-Grade Biryani at Home) into JSON."""
import json
import sys
import re
import pdfplumber
from extract_b2 import lines_of, join

from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
# Pass the PDF path as the first argument, or put the book in books/ (not committed).
PDF = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "books" / "Restaurant_Grade_Biryani_at_Home.pdf")
RANGES = [("Andhra-Style Chicken Dum Biryani", 18, 23), ("Lucknowi (Awadhi) Paneer Biryani", 24, 28),
          ("Bengaluru Donne-Style Mushroom Biryani", 29, 33), ("Chicken + Paneer for Five", 34, 36)]


def parse(pdf, title, p0, p1):
    rec = {"title": title, "page": p0, "chips": {}, "intro": [], "ingredients": [], "steps": [], "tips": [],
           "batch": False}
    mode, chip_cols, tbl = None, None, {}
    for pno in range(p0, p1 + 1):
        for ln in lines_of(pdf.pages[pno - 1]):
            t = ln["text"]
            if abs(ln["size"] - 7.8) < 0.2 and ln["x0"] > 70:
                ws = ln["words"]
                cols, cur = [], [ws[0]]
                for w in ws[1:]:
                    if w["x0"] - cur[-1]["x1"] > 20:
                        cols.append(cur)
                        cur = [w]
                    else:
                        cur.append(w)
                cols.append(cur)
                chip_cols = [(c[0]["x0"], join(c)) for c in cols]
                mode = "chips"
                continue
            if mode == "chips" and ln["font"] == "Carlito-Bold" and 7 < ln["size"] < 10.8:
                for w in ln["words"]:
                    idx = max(i for i, (x, _) in enumerate(chip_cols) if w["x0"] >= x - 3)
                    lab = chip_cols[idx][1]
                    rec["chips"][lab] = (rec["chips"].get(lab, "") + " " + w["text"]).strip()
                mode = "afterchips"
                continue
            if mode == "afterchips" and ln["font"] == "Carlito-Regular" and abs(ln["size"] - 10.5) < 0.3:
                rec["intro"].append(t)
                continue
            if ln["font"] == "Caladea-Bold" and abs(ln["size"] - 14.5) < 0.3:
                mode = {"Method": "steps"}.get(t, "ing" if t.startswith("Ingredients") else "other")
                continue
            if mode == "ing" and (t.startswith("Ingredient ") or abs(ln["size"] - 9.4) < 0.3 or
                                  abs(ln["size"] - 9.6) < 0.3 or abs(ln["size"] - 8.3) < 0.3 or
                                  (ln["font"] == "Caladea-Bold" and abs(ln["size"] - 10.5) < 0.3)):
                if t.startswith("Ingredient "):
                    rec["batch"] = "Quantity" in t
                span = tbl.setdefault(pno, [ln["top"], ln["bottom"]])
                span[0] = min(span[0], ln["top"])
                span[1] = max(span[1], ln["bottom"])
                continue
            if mode == "steps":
                fonts = {w["font"] for w in ln["words"]}
                if ln["font"] == "Carlito-Bold" and abs(ln["size"] - 11) < 0.3 and "Caladea-Bold" in fonts:
                    title_ws = [w for w in ln["words"] if w["font"] == "Caladea-Bold"]
                    meta_ws = [w for w in ln["words"] if abs(w["size"] - 8.8) < 0.3]
                    rec["steps"].append({"title": join(title_ws), "meta": join(meta_ws), "body": []})
                    sub = None
                    continue
                if rec["steps"] and ln["x0"] > 78 and ln["font"] in ("Carlito-Regular", "Carlito-Bold") and \
                        abs(ln["size"] - 10.5) < 0.3:
                    body = rec["steps"][-1]["body"]
                    if body and ln["top"] - last_top < 16 and last_kind == "body":
                        body[-1] += " " + t
                    else:
                        body.append(t)
                    last_top, last_kind = ln["top"], "body"
                    continue
                if rec["steps"] and ln["font"] == "Carlito-Bold" and abs(ln["size"] - 10) < 0.3:
                    rec["tips"].append({"title": t, "text": "", "step": len(rec["steps"])})
                    last_kind = "tip"
                    continue
                if rec["tips"] and last_kind == "tip" and abs(ln["size"] - 9.8) < 0.3:
                    rec["tips"][-1]["text"] = (rec["tips"][-1]["text"] + " " + t).strip()
                    continue
                if ln["font"] == "Carlito-Bold" and abs(ln["size"] - 8) < 0.3:
                    last_kind = "cue"
                    continue
                last_kind = "other"
    batch = rec["batch"]
    cols = [51, 396, 544] if batch else [51, 322, 396, 469, 544]
    for pno, (top, bottom) in sorted(tbl.items()):
        crop = pdf.pages[pno - 1].crop((50, max(top - 6, 0), 546, min(bottom + 9, 842)))
        rows = crop.extract_table(table_settings={
            "vertical_strategy": "explicit", "explicit_vertical_lines": cols,
            "horizontal_strategy": "lines", "intersection_tolerance": 6, "snap_tolerance": 4}) or []
        for row in rows:
            cells = [(x or "").strip() for x in row]
            if not any(cells) or cells[0].startswith("Ingredient"):
                continue
            q = (cells[1] if len(cells) > 1 else "").replace("\n", " ")
            first, _, rest = cells[0].partition("\n")
            if not q:
                rec["ingredients"].append({"group": cells[0].replace("\n", " "), "items": []})
                continue
            if not rec["ingredients"]:
                rec["ingredients"].append({"group": "", "items": []})
            rec["ingredients"][-1]["items"].append({"name": first.strip(), "note": rest.replace("\n", " ").strip(),
                                                    "q": q})
    rec["intro"] = " ".join(rec["intro"])
    for s in rec["steps"]:
        s["text"] = " ".join(s.pop("body"))
    return rec


def main():
    pdf = pdfplumber.open(PDF)
    out = [parse(pdf, *r) for r in RANGES]
    json.dump(out, open(ROOT / "data" / "b1_masters.json", "w"), indent=1, ensure_ascii=False)
    for r in out:
        print(r["title"], r["chips"], "ing:", sum(len(g["items"]) for g in r["ingredients"]), "steps:",
              len(r["steps"]), "tips:", [t["title"] for t in r["tips"]])
        print("  groups:", [(g["group"], len(g["items"])) for g in r["ingredients"]])
        for s in r["steps"][:2]:
            print("   ", s["title"], "|", s["meta"], "|", s["text"][:90])


if __name__ == "__main__":
    main()
