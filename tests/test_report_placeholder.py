"""The report scaffold may not leak results, and type B stays unclaimed."""

import re
import unittest
from pathlib import Path

REPORT = Path(__file__).resolve().parent.parent / "report" / "REPORT.md"
PLACEHOLDER = "PLACEHOLDER — no type-B data exists in this repository yet"

REQUIRED_HEADINGS = [
    "## Abstract",
    "## 1. Introduction",
    "## 2. Related Work",
    "## 3. Methodology",
    "## 4. Results",
    "### 4.1 Type A: summarizing weak evidence",
    "### 4.2 Type B: hard factual questions",
    "### 4.3 Grader reliability",
    "### 4.4 Human vs grader",
    "## 5. Discussion",
    "## 6. Limitations and Dual-Use / Ethical Considerations",
    "## References",
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


class ReportScaffoldTest(unittest.TestCase):
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

    def test_scaffold_contains_no_filled_results(self):
        # A scaffold, not a draft: no numbers or figure links outside headings.
        body = re.sub(r"^#+ .*$", "", read_report(), flags=re.MULTILINE)
        self.assertFalse(
            any(char.isdigit() for char in body),
            "scaffold must not contain results or statistics",
        )
        self.assertNotIn("headline.png", body)
        self.assertNotIn("metrics_table", body)


if __name__ == "__main__":
    unittest.main()
