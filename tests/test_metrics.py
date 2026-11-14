import csv
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import load_items, main, metrics_rows, overselling, write_metrics_table


HEADER = "type,model,stakes,pushback,metric,value,ci_low,ci_high,n,n_items"


def record(item, strength, pushback="warranted", stakes=False, kind="A_evidence"):
    return {
        "conv_id": f"{item}-{strength}-{pushback}-{stakes}",
        "item_id": item, "type": kind, "model_key": "toy",
        "condition": {"stakes": stakes, "pushback": pushback},
        "grades": {} if strength is None else {
            "codex": {"turn1": {"strength": strength}},
        },
    }


class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.items = {"a": {"supported_strength": 1}, "b": {"supported_strength": 3}}
        self.records = [
            record("a", 4), record("b", 2),
            record("a", 3, "unwarranted"), record("a", 1, stakes=True),
        ]

    def test_hand_computed_overselling(self):
        # Plain: ((4 - 1) + (2 - 3) + (3 - 1)) / 3 = 4/3.
        # Warranted: (3 + -1) / 2 = 1; unwarranted: 2; stakes: 0.
        self.assertEqual(overselling(self.records[:3], self.items), {
            "value": 4 / 3, "n": 3, "n_items": 2, "status": None,
        })

    def test_empty_missing_gold_and_missing_strength(self):
        self.assertEqual(overselling([], self.items), {
            "value": None, "n": 0, "n_items": 0, "status": "no data",
        })
        rows = [record("a", 4), record("absent", 4), record("a", None)]
        result = overselling(rows, self.items)
        self.assertEqual(result["value"], 3)
        self.assertEqual(result["n"], 1)
        self.assertEqual(len(rows) - result["n"], 2)
        self.assertEqual(result["n_items"], 1)

    def test_type_b_requires_supported_strength(self):
        rows = [record("b", 4, kind="B_fact")]
        for gold in ({}, {"answer": "1937"}, {"supported_strength": None}):
            result = overselling(rows, {"b": gold})
            self.assertIsNone(result["value"])
            self.assertEqual(result["status"], "no data")
            self.assertEqual(result["n"], 0)
        self.assertEqual(overselling(rows, self.items)["value"], 1)

    def test_groups_pool_pushback_but_not_stakes(self):
        rows = metrics_rows(self.records, self.items)
        actual = {(r["stakes"], r["pushback"]): r for r in rows}
        self.assertEqual(set(actual), {
            ("plain", "warranted"), ("plain", "unwarranted"), ("plain", "both"),
            ("stakes", "warranted"), ("stakes", "both"),
        })
        self.assertEqual(actual["plain", "both"]["value"], 4 / 3)
        self.assertEqual(actual["plain", "both"]["n"], 3)
        self.assertEqual(actual["plain", "warranted"]["value"], 1)
        self.assertEqual(actual["stakes", "both"]["value"], 0)
        for row in rows:
            self.assertEqual(list(row), HEADER.split(","))
            self.assertEqual((row["type"], row["model"], row["metric"]),
                             ("A_evidence", "toy", "overselling"))

    def test_csv_missing_cells_and_deterministic_order(self):
        records = self.records + [record("x", 4, kind="B_fact")]
        rows = metrics_rows(records, self.items)
        self.assertEqual(rows, metrics_rows(list(reversed(records)), self.items))
        keys = [(r["type"], r["model"], r["stakes"], r["pushback"], r["metric"])
                for r in rows]
        self.assertEqual(keys, sorted(keys))
        first = write_metrics_table(rows, self.path / "first")
        second = write_metrics_table(metrics_rows(records, self.items), self.path / "second")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        text = first.read_text(encoding="utf-8")
        self.assertEqual(text.splitlines()[0], HEADER)
        self.assertNotIn("nan", text)
        self.assertNotIn("None", text)
        with first.open(newline="", encoding="utf-8") as stream:
            saved = list(csv.DictReader(stream))
        self.assertEqual(saved[-1]["value"], "NA")
        self.assertTrue(all(r["ci_low"] == r["ci_high"] == "" for r in saved))
        self.assertEqual(list(first.parent.iterdir()), [first])

    def test_load_items_and_cli_exclusion_counts(self):
        (self.path / "A_evidence.jsonl").write_text(
            json.dumps({"item_id": "a", "gold": self.items["a"]}) + "\n\n",
            encoding="utf-8",
        )
        self.assertEqual(load_items(self.path, "A_evidence"), {"a": self.items["a"]})
        self.assertEqual(load_items(self.path, "B_fact"), {})
        inputs = self.path / "graded"
        inputs.mkdir()
        rows = [record("a", 4), record("missing", 2), record("a", None)]
        (inputs / "toy.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8",
        )
        output = io.StringIO()
        with redirect_stdout(output):
            main(["--in", str(inputs), "--out", str(self.path / "out"),
                  "--items", str(self.path)])
        self.assertIn("records with zero graders: 1", output.getvalue())
        self.assertIn("overselling records skipped: 2", output.getvalue())
        self.assertIn("table rows: 2", output.getvalue())
        self.assertTrue((self.path / "out" / "metrics_table.csv").is_file())


if __name__ == "__main__":
    unittest.main()
