"""The drafted report follows the template while type B stays unclaimed."""

import re
import unittest
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

REPORT = Path(__file__).resolve().parent.parent / "report" / "REPORT.md"
DOCX = REPORT.with_name("BackDown-draft.docx")
PLACEHOLDER = "PLACEHOLDER — no type-B data exists in this repository yet"

REQUIRED_HEADINGS = [
    "## Abstract",
    "## 1. Introduction",
    "## 2. Related Work",
    "## 3. Methods",
    "## 4. Results",
    "### 4.1 Type A: summarizing weak evidence",
    "### 4.2 Type B: hard factual questions",
    "### 4.3 Grader reliability",
    "### 4.4 Human vs grader",
    "## 5. Discussion and Limitations",
    "## 6. Conclusion",
    "## Code and Data",
    "## References",
    "## Appendix",
    "### Limitations and Dual-Use / Ethical Considerations",
    "## LLM Usage Statement",
]

TYPE_B_HEADING = "### 4.2 Type B: hard factual questions"


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
        self.assertTrue(REPORT.is_file(), f"missing scaffold: {REPORT}")

    def test_required_headings_present_in_order(self):
        text = read_report()
        positions = []
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text)
            positions.append(text.index(heading))
        self.assertEqual(positions, sorted(positions), "headings are out of order")

    def test_placeholder_is_visible_and_unique(self):
        text = read_report()
        self.assertEqual(text.count(PLACEHOLDER), 1)
        self.assertIn("> " + PLACEHOLDER, text)

    def test_type_b_body_is_only_the_placeholder(self):
        body = [line for line in type_b_section(read_report()) if line.strip()]
        self.assertEqual(body, ["> " + PLACEHOLDER])

    def test_type_b_section_has_no_numbers(self):
        body = "\n".join(type_b_section(read_report()))
        self.assertFalse(
            any(char.isdigit() for char in body),
            "type-B section must not carry a number",
        )

    def test_type_b_section_makes_no_claim_and_names_nobody(self):
        lowered = "\n".join(type_b_section(read_report())).lower()
        for word in (
            "daksh",
            "harshil",
            "kartik",
            "owner",
            "will deliver",
            "delivered by",
            "significant",
            "overselling",
            "discrimination",
            "capitulation",
            "mean",
            "rate",
            "%",
        ):
            self.assertNotIn(word, lowered)

    def test_abstract_is_within_template_limit(self):
        text = read_report()
        abstract = text.split("## Abstract\n", 1)[1].split("\n## ", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"\b[\w-]+\b", abstract)), 150)
        self.assertLessEqual(len(re.findall(r"\b[\w-]+\b", abstract)), 250)

    def test_numbered_figure_and_tables_have_captions(self):
        text = read_report()
        self.assertIn("![", text)
        self.assertIn("../figures/headline.png", text)
        for caption in ("**Figure 1.", "**Table 1.", "**Table 2."):
            self.assertIn(caption, text)

    def test_human_comparison_is_pending(self):
        human = read_report().split("### 4.4 Human vs grader", 1)[1].split("\n## ", 1)[0]
        self.assertIn("PENDING", human)
        self.assertNotIn("| Turn |", human)

    def test_editable_document_embeds_figure_and_tables(self):
        self.assertTrue(DOCX.is_file())
        with ZipFile(DOCX) as archive:
            self.assertIsNone(archive.testzip())
            names = set(archive.namelist())
            self.assertIn("word/media/headline.png", names)
            self.assertIn("word/styles.xml", names)
            document = ElementTree.fromstring(archive.read("word/document.xml"))
            styles = ElementTree.fromstring(archive.read("word/styles.xml"))
            self.assertIsNotNone(styles)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            text = "".join(t.text or "" for t in document.findall(".//w:t", ns))
            self.assertEqual(text.count(PLACEHOLDER), 1)
            self.assertIn("github.com/KA-1205/BackDown", text)
            self.assertEqual(len(document.findall(".//w:tbl", ns)), 2)


if __name__ == "__main__":
    unittest.main()
