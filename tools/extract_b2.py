"""Extract the recipe cards of Book 2 (Everyday Indian Meals at Home) into JSON.

Relies on the consistent fonts the book was built with:
  chapter heading  Caladea-Bold 23      card title     Caladea-Bold 17.5
  subtitle         Carlito-Italic 10    chip labels    7 pt / values Carlito-Bold 9.4
  section heads    Carlito-Bold 10.4    table rows     9.4 (notes 8.3), groups Caladea-Bold 10.5
  sub-recipe name  Carlito-Bold 11.2    tip title      Carlito-Bold 10 (box text 9.8)
"""
import json
import re
import sys
import pdfplumber

from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
# Pass the PDF path as the first argument, or put the book in books/ (not committed).
PDF = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "books" / "Everyday_Indian_Meals_at_Home.pdf")
FIRST, LAST = 27, 74  # recipe library pages


def lines_of(page):
    words = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
    words = [w for w in words if 40 < w["top"] < 800]
    words.sort(key=lambda w: (w["top"], w["x0"]))
    lines = []
    for w in words:
        w["font"] = w["fontname"].split("+")[-1]
        if lines and abs(w["top"] - lines[-1]["top"]) < 2.6:
            lines[-1]["words"].append(w)
        else:
            lines.append({"top": w["top"], "words": [w]})
    out = []
    for ln in lines:
        ws = sorted(ln["words"], key=lambda w: w["x0"])
        first = ws[0]
        out.append({"top": ln["top"], "bottom": max(w["bottom"] for w in ws), "words": ws, "x0": first["x0"],
                    "font": first["font"], "size": round(first["size"], 1), "text": join(ws)})
    return out


def join(ws):
    s = ""
    for i, w in enumerate(ws):
        if i and w["x0"] - ws[i - 1]["x1"] > 0.8:
            s += " "
        s += w["text"]
    return s


def is_(ln, font, size):
    return ln["font"] == font and abs(ln["size"] - size) < 0.25


def main():
    pdf = pdfplumber.open(PDF)
    stream = []
    for pno in range(FIRST, LAST + 1):
        for ln in lines_of(pdf.pages[pno - 1]):
            ln["page"] = pno
            stream.append(ln)

    cards, chapter, card, mode = [], None, None, None
    chip_cols = None

    def flush_par(target_list, ln, new):
        if new or not target_list:
            target_list.append(ln["text"])
        else:
            target_list[-1] += " " + ln["text"]

    for ln in stream:
        t = ln["text"]
        if is_(ln, "Caladea-Bold", 23):
            chapter = t
            mode = "chapter"
            continue
        if is_(ln, "Caladea-Bold", 17.5):
            if card and card.get("_titlecont") and ln["top"] - card["_ttop"] < 24:
                card["title"] += " " + t
                continue
            card = {"title": t, "chapter": chapter, "page": ln["page"], "sub": "", "chips": {}, "intro": [],
                    "ingredients": [], "steps": [], "cues": [], "why": "", "tips": [], "var": [], "serve": "",
                    "note": "", "subs": [], "_ttop": ln["top"], "_titlecont": True}
            cards.append(card)
            mode = "title"
            continue
        if card is None or mode == "chapter":
            continue
        card["_titlecont"] = False
        if mode == "title" and is_(ln, "Carlito-Italic", 10):
            card["sub"] = (card["sub"] + " " + t).strip()
            continue
        if abs(ln["size"] - 7) < 0.3:  # chip labels
            chip_cols = []
            ws = ln["words"]
            # group label words into columns by large gaps
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
        if mode == "chips" and is_(ln, "Carlito-Bold", 9.4):
            for w in ln["words"]:
                idx = max(i for i, (x, _) in enumerate(chip_cols) if w["x0"] >= x - 3)
                label = chip_cols[idx][1]
                card["chips"][label] = (card["chips"].get(label, "") + " " + w["text"]).strip()
            continue
        if is_(ln, "Carlito-Bold", 10.4):
            mode = {"Ingredients": "ing", "Method": "steps", "Variations and tips": "var"}.get(t, "other")
            continue
        if mode in ("chips", "intro") and is_(ln, "Carlito-Regular", 10.5):
            mode = "intro"
            card["intro"].append(t)
            continue
        if mode == "ing":
            if t.startswith("Ingredient ") or is_(ln, "Caladea-Bold", 10.5) or abs(ln["size"] - 9.4) < 0.25 \
                    or abs(ln["size"] - 8.3) < 0.25:
                if t.startswith("Ingredient "):
                    card["_batch"] = "Quantity" in t
                span = card.setdefault("_tbl", {}).setdefault(ln["page"], [ln["top"], ln["bottom"]])
                span[0] = min(span[0], ln["top"])
                span[1] = max(span[1], ln["bottom"])
                continue
        if mode == "steps":
            m = re.match(r"^(\d+)\.\s*(.*)$", t)
            if m and ln["x0"] < 62:
                card["steps"].append(m.group(2))
                continue
            if ln["x0"] > 62 and card["steps"] and ln["font"] in ("Carlito-Regular", "Carlito-Bold") and \
                    abs(ln["size"] - 10.5) < 0.3:
                card["steps"][-1] += " " + t
                continue
        # sections that can follow the method
        if re.match(r"^(LOOK|TOUCH|SMELL|TASTE|LISTEN)\b", t) and ln["font"] == "Carlito-Bold":
            card["cues"].append(t)
            mode = "cue"
            continue
        if mode == "cue" and abs(ln["size"] - 10) < 0.3 and ln["font"] == "Carlito-Regular":
            card["cues"][-1] += " " + t
            continue
        if t.startswith("Why it works:"):
            card["why"] = t[len("Why it works:"):].strip()
            mode = "why"
            continue
        if mode == "why" and abs(ln["size"] - 9.6) < 0.3:
            card["why"] += " " + t
            continue
        if ln["font"] == "Carlito-Bold" and abs(ln["size"] - 10) < 0.25:
            card["tips"].append({"title": t, "text": ""})
            mode = "tip"
            continue
        if mode == "tip" and abs(ln["size"] - 9.8) < 0.3:
            card["tips"][-1]["text"] = (card["tips"][-1]["text"] + " " + t).strip()
            continue
        if t.startswith("Serve with:"):
            card["serve"] = t[len("Serve with:"):].strip()
            mode = "serve"
            continue
        if mode == "serve" and is_(ln, "Carlito-Regular", 10.5):
            card["serve"] += " " + t
            continue
        if mode == "var":
            if t.startswith("•"):
                card["var"].append(t.lstrip("• ").strip())
                continue
            if card["var"] and abs(ln["size"] - 10.5) < 0.3:
                card["var"][-1] += " " + t
                continue
        if is_(ln, "Carlito-Italic", 9.3):
            card["note"] = (card["note"] + " " + t).strip()
            mode = "note"
            continue
        # sub-recipes (chutneys, podis, sandwiches)
        if ln["font"] == "Carlito-Bold" and abs(ln["size"] - 11.2) < 0.3:
            card["subs"].append({"name": t, "meta": "", "ing": [], "method": "", "_cols": None})
            mode = "subname"
            continue
        if card["subs"]:
            sub = card["subs"][-1]
            if abs(ln["size"] - 9) < 0.25 and mode == "subname":
                sub["meta"] = (sub["meta"] + " " + t).strip()
                continue
            if t.startswith("•") or (mode == "subing" and abs(ln["size"] - 9.6) < 0.3):
                # two-column bullets: split words by column (x < 290 left, else right)
                mode = "subing"
                left = [w for w in ln["words"] if w["x0"] < 290]
                right = [w for w in ln["words"] if w["x0"] >= 290]
                sub.setdefault("_L", [])
                sub.setdefault("_R", [])
                for side, ws in (("_L", left), ("_R", right)):
                    if not ws:
                        continue
                    txt = join(ws)
                    if txt.startswith("•"):
                        sub[side].append(txt.lstrip("• ").strip())
                    elif sub[side]:
                        sub[side][-1] += " " + txt
                continue
            if is_(ln, "Carlito-Regular", 10.5) and mode in ("subing", "submethod"):
                sub["method"] = (sub["method"] + " " + t).strip()
                mode = "submethod"
                continue
        if mode == "intro":
            continue

    for c in cards:
        batch = c.get("_batch", False)
        cols = [51, 405, 544] if batch else [51, 322, 396, 469, 544]
        for pno, (top, bottom) in sorted(c.pop("_tbl", {}).items()):
            crop = pdf.pages[pno - 1].crop((50, max(top - 6, 0), 546, min(bottom + 7, 842)))
            rows = crop.extract_table(table_settings={
                "vertical_strategy": "explicit", "explicit_vertical_lines": cols,
                "horizontal_strategy": "lines", "intersection_tolerance": 6, "snap_tolerance": 4}) or []
            for row in rows:
                cells = [(x or "").replace("\n", " ").strip() for x in row]
                if not any(cells) or cells[0] == "Ingredient":
                    continue
                q = cells[1] if len(cells) > 1 else ""
                if not q:
                    c["ingredients"].append({"group": cells[0], "items": []})
                    continue
                if not c["ingredients"]:
                    c["ingredients"].append({"group": "", "items": []})
                name, _, note = cells[0].partition(" · ")
                c["ingredients"][-1]["items"].append({"name": name.strip(), "note": note.strip(), "q": q,
                                                      "q2": cells[2] if len(cells) > 2 and not batch else ""})
        c["intro"] = " ".join(c["intro"])
        for s in c["subs"]:
            s["ing"] = s.pop("_L", []) + s.pop("_R", [])
            s.pop("_cols", None)
        for k in ("_ttop", "_titlecont"):
            c.pop(k, None)
        c["batch"] = bool(c.pop("_batch", False))
    json.dump(cards, open(ROOT / "data" / "b2_cards.json", "w"), indent=1, ensure_ascii=False)
    print(len(cards), "cards")
    for c in cards:
        print(f'{c["page"]:3d} {c["title"][:38]:38s} ing={sum(len(g["items"]) for g in c["ingredients"]):2d} '
              f'steps={len(c["steps"]):2d} var={len(c["var"])} tips={len(c["tips"])} subs={len(c["subs"])} '
              f'chips={list(c["chips"].values())}')


if __name__ == "__main__":
    main()
