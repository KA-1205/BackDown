import csv
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import grader_agreement, write_agreement_reports


def record(values, conv_id="one", kind="A_evidence", model="model"):
    return {
        "conv_id": conv_id, "type": kind, "model_key": model,
        "grades": {name: {f"turn{turn}": {"strength": value} for turn in (1, 2, 3)}
                   for name, value in zip(("claude_haiku", "codex", "glm"), values)
                   if value is not None},
    }


class AgreementTests(unittest.TestCase):
    def test_perfect_agreement(self):
        for records in ([record([2, 2, 2])],
                        [record([0, 0, 0]), record([4, 4, 4], "two")]):
            result = grader_agreement(records)["turns"][1]
            self.assertEqual(result["alpha"], 1.0)
            self.assertEqual(result["exact"], 1.0)

    def test_hand_computed_ordinal_alpha(self):
        # Units (0,0,1), (1,2,2): coincidence marginals (2,2,2), n=6.
        # delta²(0,1)=delta²(1,2)=4; delta²(0,2)=16.
        # Observed weighted sum=16, expected sum=192.
        # Do=16/6, De=192/30; alpha=1-(16/6)/(192/30)=7/12.
        result = grader_agreement(
            [record([0, 0, 1]), record([1, 2, 2], "two")])["turns"][1]
        self.assertAlmostEqual(result["alpha"], 7 / 12)
        self.assertAlmostEqual(result["exact"], 1 / 3)
        self.assertEqual(result["within_1"], 1)

    def test_missing_and_nonnumeric_values(self):
        result = grader_agreement([
            record([0, None, 2]), record([4, None, None], "two"),
            record([True, "2", float("nan")], "three"),
        ])["turns"][1]
        self.assertEqual((result["units"], result["pairs"]), (1, 1))
        self.assertEqual(result["exact"], 0)
        self.assertEqual(result["within_1"], 0)
        self.assertIsNone(grader_agreement([])["turns"][1]["alpha"])

    def test_alpha_with_mixed_coder_counts(self):
        # (0,0,1) contributes half per ordered pair; (1,2) contributes one.
        # Marginals=(2,2,1), n=5; delta²=(4,2.25,12.25) for 01,12,02.
        # Do=(8+4.5)/5=2.5; De=(32+9+49)/20=4.5; alpha=4/9.
        result = grader_agreement([
            record([0, 0, 1]), record([1, None, 2], "two"),
            record([4, None, None], "excluded"),
        ])["turns"][1]
        self.assertEqual((result["units"], result["pairs"]), (2, 4))
        self.assertAlmostEqual(result["alpha"], 4 / 9)
        self.assertEqual(result["exact"], 1 / 4)

    def test_spread_csv_and_deterministic_order(self):
        records = [record([0, None, 2], "z", "B_fact"),
                   record([0, 1, 1], "small"),
                   record([0, 3, 1], "b", model="z"),
                   record([0, 2, 4], "c"), record([0, 2, 2], "a")]
        result = grader_agreement(records)
        self.assertEqual(result, grader_agreement(list(reversed(records))))
        rows = result["disagreements"]
        self.assertEqual([(r["conv_id"], r["turn"]) for r in rows],
                         [(name, turn) for name in ("a", "c", "b", "z")
                          for turn in (1, 2, 3)])
        root = Path("/tmp/opencode/inc6")
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            _, path = write_agreement_reports(result, {"filled": 0}, directory)
            with path.open(newline="") as stream:
                saved = list(csv.DictReader(stream))
            self.assertEqual(saved[-1], {
                "conv_id": "z", "turn": "3", "spread": "2",
                "claude_haiku": "0", "codex": "", "glm": "2",
            })
