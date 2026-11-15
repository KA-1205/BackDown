from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import load_graded, main


def record(conv_id="one", **changes):
    return {
        "conv_id": conv_id, "type": "A_evidence", "model_key": "gemini_lite",
        "condition": {"stakes": False, "pushback": "warranted", "variant": "natural"},
        "grades": {"codex": {}}, **changes,
    }


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def write(self, name, rows):
        (self.path / name).write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )

    def test_latest_non_error_wins_across_sorted_files(self):
        self.write("b.jsonl", [record(marker="latest"), record(error="failed")])
        self.write("a.jsonl", [record(marker="first"), record(marker="middle")])
        result = load_graded(self.path)
        self.assertEqual(result["records"], [record(marker="latest")])
        self.assertEqual(result["duplicates"], 2)
        self.assertEqual(result["skipped_errors"], 1)
        self.assertEqual(len(result["files_read"]), 2)

    def test_errors_including_falsey_values_are_skipped(self):
        self.write("a.jsonl", [
            record("failed", error="failure"), record("empty", error=""),
            record("false", error=False), record("ok", error=None),
        ])
        result = load_graded(self.path)
        self.assertEqual([r["conv_id"] for r in result["records"]], ["ok"])
        self.assertEqual(result["skipped_errors"], 3)

    def test_empty_and_missing_directory(self):
        for path in (self.path, self.path / "missing"):
            result = load_graded(path)
            for key in ("records", "files_read", "malformed_examples"):
                self.assertEqual(result[key], [])
            for key in ("by_type", "by_model", "by_condition", "grader_coverage"):
                self.assertEqual(result[key], {})
            for key in ("duplicates", "skipped_errors", "malformed_lines"):
                self.assertEqual(result[key], 0)

    def test_malformed_lines_counted_and_examples_capped(self):
        path = self.path / "a.jsonl"
        path.write_text("\n" + "{broken\n" * 7 + json.dumps(record()) + "\n")
        result = load_graded(self.path)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["malformed_lines"], 7)
        self.assertEqual(result["malformed_examples"],
                         [f"{path}:{line}" for line in range(2, 7)])

    def test_non_record_json_is_skipped(self):
        self.write("a.jsonl", [None, [], {}, record()])
        result = load_graded(self.path)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["malformed_lines"], 3)

    def test_counts_use_deduped_records_and_actual_graders(self):
        rows = [
            record(),
            record("two", type="B_fact", model_key="gpt_oss",
                   condition={"stakes": True, "pushback": "unwarranted"},
                   grades={"glm": {}, "custom": {}}),
            record("three", grades={}),
        ]
        self.write("a.jsonl", [rows[0], *rows, record("error", error="failed")])
        result = load_graded(self.path)
        self.assertEqual(result["by_type"], {"A_evidence": 2, "B_fact": 1})
        self.assertEqual(result["by_model"], {"gemini_lite": 2, "gpt_oss": 1})
        self.assertEqual(result["by_condition"],
                         {(False, "warranted"): 2, (True, "unwarranted"): 1})
        self.assertEqual(result["grader_coverage"], {"codex": 1, "custom": 1, "glm": 1})

    def test_default_run_excludes_explicit_confidence_ablation(self):
        self.write("natural.jsonl", [record("natural")])
        self.write("A_evidence__seed1__explicit_confidence.jsonl", [
            record("ablation", condition={
                "stakes": False, "pushback": "warranted",
                "variant": "explicit_confidence",
            }),
        ])
        self.write("mixed.jsonl", [
            record("mixed-ablation", condition={
                "stakes": False, "pushback": "warranted",
                "variant": "explicit_confidence",
            }),
        ])
        natural = load_graded(self.path)
        self.assertEqual([r["conv_id"] for r in natural["records"]], ["natural"])
        self.assertEqual(len(natural["files_read"]), 2)
        explicit = load_graded(self.path, variant="explicit_confidence")
        self.assertEqual([r["conv_id"] for r in explicit["records"]],
                         ["ablation", "mixed-ablation"])

    def test_default_run_uses_seed_one_only(self):
        self.write("A_evidence__x__seed1.jsonl", [record("seed-one")])
        self.write("A_evidence__x__seed2.jsonl", [record("seed-two", seed=2)])
        self.write("mixed.jsonl", [record("mixed-two", seed=2), record("mixed-one", seed=1)])
        first = load_graded(self.path)
        self.assertEqual([r["conv_id"] for r in first["records"]],
                         ["mixed-one", "seed-one"])
        self.assertEqual(len(first["files_read"]), 2)
        second = load_graded(self.path, seed=2)
        self.assertEqual([r["conv_id"] for r in second["records"]],
                         ["mixed-two", "seed-two"])
        self.assertEqual(len(second["files_read"]), 2)

    def test_cli_creates_empty_output_and_stable_no_data_summary(self):
        self.write("a.jsonl", [record()])
        output = self.path / "output"
        summaries = []
        for _ in range(2):
            stream = io.StringIO()
            with redirect_stdout(stream):
                main(["--in", str(self.path), "--out", str(output)])
            summaries.append(stream.getvalue())
        self.assertTrue(output.is_dir())
        self.assertEqual(list(output.iterdir()), [output / "metrics_table.csv"])
        self.assertEqual(
            (output / "metrics_table.csv").read_text(encoding="utf-8").splitlines()[0],
            "type,model,stakes,pushback,metric,value,ci_low,ci_high,n,n_items",
        )
        self.assertEqual(summaries[0], summaries[1])
        for line in ("total records: 1", "type A_evidence: 1",
                     "type B_fact: no data", "grader codex: 1",
                     "condition plain × warranted: 1"):
            self.assertIn(line, summaries[0].splitlines())


if __name__ == "__main__":
    unittest.main()
