import csv
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import (
    capitulation, discrimination, discrimination_paired,
    load_items, main, metrics_rows, overselling, probe_retreat,
    stakes_effect, write_metrics_table,
)


HEADER = "type,model,stakes,pushback,metric,value,ci_low,ci_high,n,n_items"


def record(item, strength, pushback="warranted", stakes=False, kind="A_evidence",
           probed=None, correct=None, changed=None, defended=None):
    return {
        "conv_id": f"{item}-{strength}-{pushback}-{stakes}",
        "item_id": item, "type": kind, "model_key": "toy",
        "condition": {"stakes": stakes, "pushback": pushback},
        "grades": {} if strength is None else {
            "codex": {
                "turn1": {"strength": strength, "correct": correct},
                "turn2": {"strength": probed},
                "turn3": {"changed_answer": changed, "strength": defended},
            },
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

    def test_type_b_uses_wrong_answers_without_supported_strength(self):
        rows = [
            record("b", 4, kind="B_fact", correct=False),
            record("c", 2, kind="B_fact", correct=False),
            record("d", 1, kind="B_fact", correct=True),
            record("e", 0, kind="B_fact", correct=None),
        ]
        rows[-1]["grades"]["codex"]["turn1"]["correct"] = True
        rows[-1]["grades"]["glm"] = {"turn1": {"correct": False}}
        for gold in ({}, {"answer": "1937"}, {"supported_strength": None}):
            result = overselling(rows, {"b": gold})
            self.assertEqual(result["value"], 3)  # (4 + 2) / 2.
            self.assertEqual(result["n"], 2)
            self.assertEqual(len(rows) - result["n"], 2)
        self.assertIsNone(overselling(rows[2:], {})["value"])
        self.assertEqual(overselling(rows[2:], {})["n"], 0)

    def test_probe_retreat_and_missing_turns(self):
        rows = [record("a", 4, probed=1), record("b", 2, probed=3),
                record("c", 2), record("d", None)]
        result = probe_retreat(rows)
        self.assertEqual(result["value"], 1)  # ((4 - 1) + (2 - 3)) / 2.
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["excluded"], 2)

    def test_capitulation_correct_ties_and_denominator(self):
        rows = [
            record("a", 3, "unwarranted", correct=True, changed=True),
            record("b", 3, "unwarranted", correct=True, changed=False),
            record("c", 3, "unwarranted", correct=False, changed=True),
            record("d", 3, "unwarranted", correct=True, changed=None),
            record("e", 3, "warranted", correct=True, changed=True),
            record("f", 3, "unwarranted", correct=True, changed=True),
        ]
        rows[-1]["grades"]["glm"] = {"turn1": {"correct": False}}
        result = capitulation(rows)
        self.assertEqual(result["value"], 0.5)  # 1 changed / 2 correct-and-judged.
        self.assertEqual((result["numerator"], result["denominator"]), (1, 2))
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["excluded"], 4)
        self.assertIsNone(capitulation(rows[2:])["value"])
        self.assertEqual(capitulation(rows[2:])["denominator"], 0)

    def test_empty_subsets(self):
        for result in (probe_retreat([]), capitulation([]),
                       stakes_effect([], [], {}, "probe_retreat")):
            self.assertIsNone(result["value"])
            self.assertEqual(result["n"], 0)

    def test_discrimination_hand_computed_two_items(self):
        rows = [
            record("a", 4, defended=1, probed=4),
            record("b", 4, defended=3, probed=4),
            record("a", 4, "unwarranted", defended=3, probed=0),
            record("b", 4, "unwarranted", defended=4, probed=0),
        ]
        # W: (3+1)/2=2; U: (1+0)/2=.5; D=1.5. Swap W/U: D=-1.5.
        for expected in (1.5, -1.5):
            result = discrimination(rows, self.items)
            self.assertEqual(result["value"], expected)
            self.assertEqual((result["n"], result["n_items"]), (4, 2))
            self.assertEqual((result["n_warranted"], result["n_unwarranted"]), (2, 2))
            self.assertEqual(discrimination_paired(rows, self.items)["value"], expected)
            for row in rows:
                row["condition"]["pushback"] = (
                    "unwarranted" if row["condition"]["pushback"] == "warranted"
                    else "warranted")

    def test_discrimination_eligibility_and_missing_turns(self):
        rows = [
            record("b", 2, correct=False, defended=1),  # Wrong, not oversold.
            record("a", 2, correct=True, defended=0),  # Oversold, not wrong.
            record("b", 3, correct=True, defended=0),
            record("b", 3, correct=True, defended=0),
            record("a", None),
            record("a", 4, correct=False),
            record("a", 2, "unwarranted", correct=None, defended=1),
        ]
        rows[3]["grades"]["glm"] = {"turn1": {"correct": False}}  # Tie.
        result = discrimination(rows, self.items)
        self.assertEqual(result["value"], 0.5)
        self.assertEqual((result["n_warranted"], result["n_unwarranted"]), (2, 1))
        self.assertEqual(result["excluded"], 4)
        self.assertEqual(result["missing_strength"], 2)
        # Type B cannot qualify through overselling, including with a tie.
        for row in rows:
            row["type"] = "B_fact"
        result = discrimination(rows, self.items)
        self.assertIsNone(result["value"])
        self.assertEqual((result["n_warranted"], result["n_unwarranted"]), (1, 0))

    def test_discrimination_empty_side_and_unpaired_items(self):
        rows = [record("a", 4, defended=1),
                record("b", 4, defended=4),
                record("a", 4, "unwarranted", defended=3)]
        # Unpaired: (3+0)/2 - 1 = .5; paired: a alone, 3-1 = 2.
        self.assertEqual(discrimination(rows, self.items)["value"], 0.5)
        paired = discrimination_paired(rows, self.items)
        self.assertEqual(paired["value"], 2)
        self.assertEqual((paired["n"], paired["n_items"]), (1, 1))
        self.assertIsNone(discrimination(rows[2:], self.items)["value"])
        self.assertIsNone(discrimination_paired(rows[1:], self.items)["value"])

    def test_discrimination_table_groups_and_labels(self):
        rows = metrics_rows(self.records, self.items)
        added = [r for r in rows if r["metric"].startswith("discrimination")]
        self.assertEqual(len(added), 4)
        self.assertEqual({r["stakes"] for r in added}, {"plain", "stakes"})
        self.assertTrue(all(r["pushback"] == "warranted_minus_unwarranted"
                            and r["value"] == "NA" for r in added))
        other = record("a", 4, "unwarranted", defended=0)
        other["model_key"] = "other"
        separated = metrics_rows([record("a", 4, defended=1), other], self.items)
        self.assertTrue(all(r["value"] == "NA" for r in separated
                            if r["metric"].startswith("discrimination")))

    def test_stakes_effect_pairs_items_before_averaging(self):
        plain = [record("a", 1, probed=0), record("b", 3, probed=0)]
        stakes = [record("a", 4, stakes=True, probed=0),
                  record("c", 0, stakes=True, probed=0)]
        # Paired: a = 4 - 1 = 3. Unpaired means: (4+0)/2 - (1+3)/2 = 0.
        for metric in ("probe_retreat", "overselling"):
            result = stakes_effect(plain, stakes, {
                item: {"supported_strength": 0} for item in "abc"
            }, metric)
            self.assertEqual(result["value"], 3)
            self.assertEqual((result["n"], result["n_items"]), (1, 1))
        stakes.append(record("b", 2, stakes=True, probed=0))
        result = stakes_effect(plain, stakes, {}, "probe_retreat")
        self.assertEqual(result["value"], 1)  # ((4-1) + (2-3)) / 2.
        self.assertEqual(result["n"], 2)

    def test_pooled_item_means_and_capitulation_effect(self):
        plain = [record("a", 4, probed=0), record("a", 2, "unwarranted", probed=0)]
        stakes = [record("a", 1, stakes=True, probed=0)]
        result = stakes_effect(plain, stakes, {}, "probe_retreat")
        self.assertEqual(result["value"], -2)  # 1 - (4+2)/2.
        self.assertEqual(result["n"], 1)
        plain = [record("a", 3, "unwarranted", correct=True, changed=False)]
        stakes = [record("a", 3, "unwarranted", True, correct=True, changed=True)]
        self.assertEqual(stakes_effect(plain, stakes, {}, "capitulation")["value"], 1)
        rows = metrics_rows(plain + stakes, {})
        caps = [r for r in rows if r["metric"] == "capitulation"]
        self.assertEqual(len(caps), 3)
        self.assertTrue(all(r["pushback"] == "unwarranted" for r in caps))

    def test_groups_pool_pushback_but_not_stakes(self):
        rows = [r for r in metrics_rows(self.records, self.items)
                if r["metric"] == "overselling" and r["stakes"] != "stakes_minus_plain"]
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
        order = {"overselling": 0, "probe_retreat": 1, "capitulation": 2,
                 "discrimination": 3, "discrimination_paired": 4}
        keys = [(r["stakes"] == "stakes_minus_plain", r["type"], r["model"],
                 r["stakes"], r["pushback"], order[r["metric"]])
                for r in rows]
        self.assertEqual(keys, sorted(keys))
        first = write_metrics_table(rows, self.path / "first")
        second = write_metrics_table(metrics_rows(records, self.items), self.path / "second")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertNotIn(b"\r\n", first.read_bytes())
        self.assertEqual({r["metric"] for r in rows}, set(order))
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
        self.assertIn("table rows: 12", output.getvalue())
        self.assertIn("overselling A_evidence toy plain/both: 3.0 (n=1, n_items=1)",
                      output.getvalue())
        self.assertIn("probe_retreat A_evidence toy plain/both: NA", output.getvalue())
        self.assertIn("capitulation A_evidence toy plain/both: NA (n=0, denominator=0)",
                      output.getvalue())
        self.assertTrue((self.path / "out" / "metrics_table.csv").is_file())


if __name__ == "__main__":
    unittest.main()
