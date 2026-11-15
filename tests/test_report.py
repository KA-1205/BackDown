"""The drafted report covers both types and keeps pending validation explicit."""

import re
import unittest
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

REPORT = Path(__file__).resolve().parent.parent / "report" / "REPORT.md"
DOCX = REPORT.with_name("BackDown-draft.docx")

REQUIRED_HEADINGS = [
    "## Abstract",
    "## 1. Introduction",
    "## 2. Related Work",
    "## 3. Methods",
    "## 4. Results",
    "### 4.1 Type A: summarizing weak evidence",
    "### 4.2 Type B: short factual questions",
    "### 4.3 Rotation check (seed 2)",
    "### 4.4 Grader reliability",
    "### 4.5 Human vs grader",
    "## 5. Discussion and Limitations",
    "## 6. Conclusion",
    "## Code and Data",
    "## References",
    "## Appendix",
    "### Limitations and Dual-Use / Ethical Considerations",
    "## LLM Usage Statement",
]

TYPE_B_HEADING = "### 4.2 Type B: short factual questions"


def read_report():
    return REPORT.read_text(encoding="utf-8")


def type_b_section(text):
    """Return the lines of the type-B section, excluding the heading."""
    lines = text.splitlines()
    start = lines.index(TYPE_B_HEADING) + 1
    end = start
    while end < len(lines) and not lines[end].startswith("#"):
        end += 1
    return lines[start:end]


class ReportDraftTest(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.is_file(), f"missing report: {REPORT}")

    def test_required_headings_present_in_order(self):
        text = read_report()
        positions = []
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text)
            positions.append(text.index(heading))
        self.assertEqual(positions, sorted(positions), "headings are out of order")

    def test_no_stale_type_b_placeholder(self):
        text = read_report()
        self.assertNotIn("PLACEHOLDER", text)
        self.assertNotIn("no type-B data", text)

    def test_type_b_section_reports_verified_results(self):
        body = "\n".join(type_b_section(read_report()))
        for value in ("3.887", "3.442", "1.367", "27/80", "9/80"):
            self.assertIn(value, body)
        self.assertNotIn("TODO", body)

    def test_abstract_is_within_template_limit(self):
        text = read_report()
        abstract = text.split("## Abstract\n", 1)[1].split("\n## ", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"\b[\w-]+\b", abstract)), 150)
        self.assertLessEqual(len(re.findall(r"\b[\w-]+\b", abstract)), 250)

    def test_numbered_figures_and_tables_have_captions(self):
        text = read_report()
        self.assertIn("../figures/headline.png", text)
        self.assertIn("../figures/headline_B_fact.png", text)
        for caption in ("**Figure 1.", "**Figure 2.",
                        "**Table 1.", "**Table 2.", "**Table 3.", "**Table 4."):
            self.assertIn(caption, text)

    def test_human_comparison_reports_available_labels_and_pending_validation(self):
        human = read_report().split("### 4.5 Human vs grader", 1)[1].split("\n## ", 1)[0]
        self.assertIn("PENDING", human)
        self.assertIn("**Table 4.", human)
        self.assertIn("| Type A | All turns | 36 | 0.722222 | 0.361111 | 0.916667 |", human)
        self.assertIn("| Type B | All turns | 36 | 0.388889 | 0.666667 | 0.944444 |", human)
        self.assertIn("| All labels | All turns | 72 | 0.555556 | 0.513889 | 0.930556 |", human)
        self.assertIn("132 strength rows remain blank", human)
        self.assertIn("No inter-human agreement estimate is available", human)

    def test_editable_document_embeds_figures_and_tables(self):
        self.assertTrue(DOCX.is_file())
        with ZipFile(DOCX) as archive:
            self.assertIsNone(archive.testzip())
            names = set(archive.namelist())
            self.assertIn("word/media/headline.png", names)
            self.assertIn("word/media/headline_B_fact.png", names)
            self.assertIn("word/styles.xml", names)
            document = ElementTree.fromstring(archive.read("word/document.xml"))
            styles = ElementTree.fromstring(archive.read("word/styles.xml"))
            self.assertIsNotNone(styles)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text = "".join(t.text or "" for t in document.findall(".//w:t", ns))
            self.assertNotIn("PLACEHOLDER", text)
            self.assertIn("github.com/KA-1205/BackDown", text)
            self.assertIn("3.887", text)
            self.assertEqual(len(document.findall(".//w:tbl", ns)), 4)
            self.assertEqual(len(document.findall(".//w:drawing", ns)), 2)


if __name__ == "__main__":
    unittest.main()
