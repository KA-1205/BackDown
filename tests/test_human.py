import csv
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import compare_human, grader_agreement, write_agreement_reports


class HumanTests(unittest.TestCase):
    def setUp(self):
        root = Path("/tmp/opencode/inc6")
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.records = [{
            "conv_id": "one", "type": "A_evidence", "model_key": "toy",
            "grades": {
                "claude_haiku": {"turn1": {"strength": 0}, "turn2": {"strength": 2}},
                "codex": {"turn1": {"strength": 2}},
                "glm": {"turn1": {"strength": 4}, "turn2": {"strength": 2}},
            },
        }]

    def labels(self, rows, name="labels_toy.csv"):
        with (self.path / name).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["label_id", "conv_id", "labeler", "turn", "strength",
                             "correct", "changed_answer", "note"])
            for conv_id, turn, strength in rows:
                writer.writerow(["id", conv_id, "human", turn, strength, "", "", ""])

    def test_blank_labels(self):
        self.labels([("one", 1, ""), ("one", 2, " ")])
        result = compare_human(self.records, self.path)
        path, _ = write_agreement_reports(grader_agreement(self.records), result, self.path)
        text = path.read_text()
        self.assertIn("No human labels yet.", text.splitlines())
        self.assertNotIn("NaN", text)
        self.assertEqual(result["filled"], 0)

    def test_known_errors_and_all_label_files(self):
        self.labels([("one", 1, 1)])
        self.labels([("one", 2, 2)], "labels_second.csv")
        result = compare_human(self.records, self.path)
        self.assertEqual(result["overall"]["combined"],
                         {"n": 2, "mae": 0.5, "exact": 0.5, "within_1": 1})
        self.assertEqual(result["overall"]["glm"],
                         {"n": 2, "mae": 1.5, "exact": 0.5, "within_1": 0.5})
        self.assertEqual(result["overall"]["codex"]["n"], 1)
        self.assertEqual(result["turns"][1]["combined"]["mae"], 1)
        self.assertEqual(result["turns"][2]["combined"]["exact"], 1)

    def test_unmatched_rows_ignored_and_counted(self):
        self.labels([("absent", 1, 2), ("one", 4, 2), ("one", 3, 2),
                     ("one", "invalid", 2), ("one", 1, 1)])
        result = compare_human(self.records, self.path)
        self.assertEqual(result["unmatched"], 4)
        self.assertEqual(result["overall"]["combined"]["n"], 1)

    def test_invalid_strengths_counted_without_nan(self):
        self.labels([("one", 1, "nan"), ("one", 1, "bad")])
        result = compare_human(self.records, self.path)
        self.assertEqual(result["invalid"], 2)
        self.assertEqual(result["overall"]["combined"]["n"], 0)
