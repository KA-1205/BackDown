import csv
from pathlib import Path
import tempfile
import unittest

from backdown.analyze import write_headline_figure


class FigureTests(unittest.TestCase):
    def setUp(self):
        root = Path("/tmp/opencode/inc7")
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        with Path("figures/metrics_table.csv").open() as stream:
            self.rows = list(csv.DictReader(stream))

    def test_png_signature_and_size(self):
        path = write_headline_figure(self.rows, self.path)
        self.assertTrue(path.exists())
        self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertGreater(path.stat().st_size, 20 * 1024)

    def test_repeated_render_is_byte_identical(self):
        first = write_headline_figure(self.rows, self.path / "first")
        second = write_headline_figure(self.rows, self.path / "second")
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_absent_condition_and_missing_metric_render(self):
        reduced = [row for row in self.rows
                   if not (row["model"] == "nemotron" and row["stakes"] == "stakes")
                   and not (row["model"] == "gpt_oss" and row["stakes"] == "plain"
                            and row["metric"] == "discrimination")]
        path = write_headline_figure(reduced, self.path)
        self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
