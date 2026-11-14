import io
from contextlib import redirect_stdout
import unittest

from backdown.analyze import (
    add_bootstrap_cis, bootstrap_ci, metrics_rows, percentile,
)
from test_metrics import record


class BootstrapTests(unittest.TestCase):
    def test_repeatability_and_bracketing(self):
        clusters = {"a": (0, 1), "b": (2, 1), "c": (4, 1)}
        first = bootstrap_ci(clusters, "mean", 2, "toy")
        self.assertEqual(first, bootstrap_ci(clusters, "mean", 2, "toy"))
        self.assertLessEqual(first[0], 2)
        self.assertGreaterEqual(first[1], 2)

    def test_single_item(self):
        self.assertEqual(
            bootstrap_ci({"a": (6, 3)}, "mean", 2, "single"), (2.0, 2.0))

    def test_percentile_interpolation(self):
        self.assertAlmostEqual(percentile([0, 10, 20, 30], 0.025), 0.75)
        self.assertAlmostEqual(percentile([0, 10, 20, 30], 0.975), 29.25)
        self.assertEqual(percentile([7], 0.975), 7)

    def test_paired_metrics_keep_repeats_in_item_clusters(self):
        # Both items have paired difference 1, despite variation within item a.
        # Resampling records independently can break the pairs and yield -1 or 3.
        records = [
            record("a", 4, defended=0, probed=0),
            record("a", 4, defended=4, probed=4),
            record("a", 4, "unwarranted", defended=3, probed=3),
            record("b", 4, defended=2, probed=2),
            record("b", 4, "unwarranted", defended=3, probed=3),
        ]
        rows = metrics_rows(records, {"a": {"supported_strength": 0},
                                     "b": {"supported_strength": 0}})
        add_bootstrap_cis(rows, records, {"a": {"supported_strength": 0},
                                        "b": {"supported_strength": 0}})
        paired = next(r for r in rows if r["metric"] == "discrimination_paired"
                      and r["stakes"] == "plain")
        self.assertEqual((paired["value"], paired["ci_low"], paired["ci_high"]),
                         (1, 1.0, 1.0))
        # Repeat averaging for stakes effects must also precede resampling.
        plain = [record("a", 4, probed=0), record("a", 4, probed=4),
                 record("b", 4, probed=2)]
        stakes = [record("a", 4, stakes=True, probed=1),
                  record("b", 4, stakes=True, probed=1)]
        rows = metrics_rows(plain + stakes, {})
        add_bootstrap_cis(rows, plain + stakes, {})
        effect = next(r for r in rows if r["metric"] == "probe_retreat"
                      and r["stakes"] == "stakes_minus_plain"
                      and r["pushback"] == "both")
        self.assertEqual((effect["value"], effect["ci_low"], effect["ci_high"]),
                         (1, 1.0, 1.0))

    def test_na_row(self):
        records = [record("a", None)]
        rows = metrics_rows(records, {})
        add_bootstrap_cis(rows, records, {})
        self.assertTrue(all(r["value"] == r["ci_low"] == r["ci_high"] == "NA"
                            for r in rows))

    def test_row_processing_order_independence(self):
        records = [record("a", 4, probed=1), record("b", 1, probed=2)]
        items = {"a": {"supported_strength": 0}, "b": {"supported_strength": 0}}
        forward = metrics_rows(records, items)
        reverse = list(reversed(metrics_rows(records, items)))
        add_bootstrap_cis(forward, records, items)
        add_bootstrap_cis(reverse, records, items)
        self.assertEqual(forward, list(reversed(reverse)))

    def test_base_rows_weight_records_within_item(self):
        records = [record("a", 4, probed=0), record("a", 4, probed=0),
                   record("b", 1, probed=0)]
        rows = metrics_rows(records, {})
        add_bootstrap_cis(rows, records, {})
        row = next(r for r in rows if r["metric"] == "probe_retreat"
                   and r["stakes"] == "plain" and r["pushback"] == "both")
        self.assertEqual((row["value"], row["ci_low"], row["ci_high"]), (3, 1, 4))

    def test_invalid_discrimination_resamples_warn_and_preserve_point(self):
        output = io.StringIO()
        # Each side occurs on a different item: roughly half of draws are invalid.
        with redirect_stdout(output):
            interval = bootstrap_ci(
                {"a": (2, 1, 0, 0), "b": (0, 0, 1, 1)},
                "discrimination", 1, "sparse-row")
        self.assertEqual(interval, ("NA", "NA"))
        self.assertIn("sparse-row", output.getvalue())
        self.assertEqual(len(output.getvalue().splitlines()), 1)

    def test_point_consistency_is_asserted(self):
        with self.assertRaises(AssertionError):
            bootstrap_ci({"a": (1, 1), "b": (3, 1)}, "mean", 99, "bad-row")


if __name__ == "__main__":
    unittest.main()
