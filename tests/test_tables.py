import csv
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import METRICS_COLUMNS, write_metrics_markdown


class TableTests(unittest.TestCase):
    def setUp(self):
        root = Path("/tmp/opencode/inc7")
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        with Path("figures/metrics_table.csv").open() as stream:
            self.rows = list(csv.DictReader(stream))

    def cells(self, path):
        return [[cell.strip() for cell in line.strip("|").split("|")]
                for line in path.read_text().splitlines() if line.startswith("|")]

    def test_header_count_and_row_order(self):
        path = write_metrics_markdown(self.rows, self.temp.name)
        self.assertTrue(path.exists())
        cells = self.cells(path)
        self.assertEqual(cells[0], list(METRICS_COLUMNS))
        self.assertEqual(len(cells) - 2, len(self.rows))
        self.assertEqual([row[:5] for row in cells[2:]],
                         [[row[key] for key in METRICS_COLUMNS[:5]] for row in self.rows])

    def test_missing_values_are_explicit_na(self):
        for missing in ("NA", None, float("nan"), ""):
            row = dict(self.rows[0], value=missing, ci_low=missing, ci_high=missing)
            cells = self.cells(write_metrics_markdown([row], self.temp.name))[2]
            self.assertEqual(cells[5:8], ["NA"] * 3)
            self.assertNotIn("", cells)
            self.assertNotIn("nan", cells)

    def test_three_decimal_display_and_method(self):
        path = write_metrics_markdown(self.rows, self.temp.name)
        cells = self.cells(path)
        self.assertEqual(cells[2][5], "1.675")
        self.assertEqual(cells[6][5], "0.682")
        self.assertEqual(cells[2][6:8], ["1.325", "2.025"])
        self.assertIn("95% item-cluster percentile bootstrap", path.read_text())
        self.assertIn("1000 resamples, seed 12345", path.read_text())
