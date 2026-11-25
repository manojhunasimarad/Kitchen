"""Prep-ahead and batch-prep data stay consistent with the recipes they describe."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "data.json").read_text(encoding="utf-8"))
R = {r["id"]: r for r in DATA["recipes"]}


def names(r):
    return [i["name"] for g in r["ingredients"] if isinstance(g, dict) for i in g["items"]]


class PrepAhead(unittest.TestCase):
    def test_every_task_points_at_a_real_ingredient(self):
        for rid, tasks in DATA["advance"]["recipes"].items():
            self.assertIn(rid, R)
            for t in tasks:
                self.assertIn(t["kind"], {"soak", "sprout", "marinate", "rest"})
                self.assertTrue(any(t["item"].lower() in n.lower() for n in names(R[rid])), (rid, t["item"]))
                lo, hi = t["hours"]
                self.assertLessEqual(lo, hi, rid)
                if t["kind"] == "marinate":
                    self.assertLessEqual(t["roomMax"], 2, rid + ": never more than 2 hours without a fridge")
                if "max" in t:
                    self.assertGreaterEqual(t["max"], hi, rid)

    def test_long_soaks_in_the_recipe_text_are_covered(self):
        covered = set(DATA["advance"]["recipes"])
        for r in DATA["recipes"]:
            text = " ".join([r.get("time", "")] + r["steps"]).lower()
            if re.search(r"soak\w*[^.]{0,40}\b([4-9]|1\d)\s*(–\s*\d+\s*)?hours|overnight soak|sprout", text) and r["course"] != "side":
                self.assertIn(r["id"], covered, r["id"] + " needs soaking or sprouting but has no prep-ahead entry")

    def test_batch_components_are_valid(self):
        for c in DATA["batch"]["components"]:
            re.compile(c["match"], re.I)
            self.assertGreater(c["fridgeDays"], 0)
            self.assertTrue(c["how"] and c["noFridge"])
        garlic_paste = next(c for c in DATA["batch"]["components"] if c["id"] == "gg")
        self.assertEqual(garlic_paste["roomHours"], 0, "garlic in oil must be refrigerated")


if __name__ == "__main__":
    unittest.main()
