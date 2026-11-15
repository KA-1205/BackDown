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
    "### 4.1 Evidence: weak and ambiguous study summaries",
    "### 4.2 Fact: short factual questions",
    "### 4.3 Rotation check (seed 2)",
    "### 4.4 Grader reliability",
    "### 4.5 Human versus grader",
    "### 4.6 Explicit-confidence ablation",
    "## 5. Discussion and Limitations",
    "## 6. Conclusion",
    "## 7. Future Work",
    "## Code and Data",
    "## References",
    "## Appendix",
    "### Limitations and Dual-Use / Ethical Considerations",
    "## LLM Usage Statement",
]

FACT_HEADING = "### 4.2 Fact: short factual questions"


def read_report():
    return REPORT.read_text(encoding="utf-8")


def fact_section(text):
    """Return the lines of the Fact section, excluding the heading."""
    lines = text.splitlines()
    start = lines.index(FACT_HEADING) + 1
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

    def test_no_stale_placeholders(self):
        text = read_report()
        self.assertNotIn("PLACEHOLDER", text)
        self.assertNotIn("no type-B data", text)

    def test_fact_section_reports_verified_results(self):
        body = "\n".join(fact_section(read_report()))
        for value in ("3.887", "3.442", "1.367", "27/80", "9/80"):
            self.assertIn(value, body)
        self.assertNotIn("TODO", body)

    def test_sets_use_display_names(self):
        text = read_report()
        self.assertIn("**Evidence** (`A_evidence`)", text)
        self.assertIn("**Fact** (`B_fact`)", text)
        self.assertNotIn("Type A", text)
        self.assertNotIn("Type B", text)
        self.assertNotIn("type A", text)
        self.assertNotIn("type B", text)

    def test_sprint_attribution_links_source(self):
        text = read_report()
        self.assertIn("**MisleadBench** and **FlipRate**", text)
        self.assertIn("https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15", text)

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
                        "**Table 1.", "**Table 2.", "**Table 3.", "**Table 4.",
                        "**Table 5.", "**Table 6."):
            self.assertIn(caption, text)

    def test_human_comparison_reports_complete_labels_and_limits(self):
        human = read_report().split("### 4.5 Human versus grader", 1)[1].split("\n## ", 1)[0]
        self.assertIn("**204 rows, none blank**", human)
        self.assertIn("**Table 4.", human)
        self.assertIn("| Harshil | Evidence | 33 | 0.454545 | 0.606061 | 0.939394 |", human)
        self.assertIn("| Daksh | Evidence | 33 | 0.636364 | 0.484848 | 0.878788 |", human)
        self.assertIn("| Kartik | Evidence | 36 | 0.722222 | 0.361111 | 0.916667 |", human)
        self.assertIn("| Harshil | Fact | 33 | 0.393939 | 0.818182 | 0.909091 |", human)
        self.assertIn("| Daksh | Fact | 33 | 0.242424 | 0.787879 | 0.969697 |", human)
        self.assertIn("| Kartik | Fact | 36 | 0.388889 | 0.666667 | 0.944444 |", human)
        self.assertIn("exact 0.267", human)
        self.assertIn("exact 0.733", human)
        self.assertIn("not external validation", human)
        self.assertNotIn("PENDING", human)

    def test_ablation_section_reports_both_experiments(self):
        ablation = read_report().split("### 4.6 Explicit-confidence ablation", 1)[1].split("\n## ", 1)[0]
        self.assertIn("#### 4.6.1 Evidence", ablation)
        self.assertIn("#### 4.6.2 Fact", ablation)
        self.assertIn("**Table 5.", ablation)
        self.assertIn("**Table 6.", ablation)
        self.assertIn("2.35 → 3.90", ablation)
        self.assertIn("3.19 → 2.92", ablation)

    def test_llm_statement_names_assistants(self):
        statement = read_report().split("## LLM Usage Statement", 1)[1]
        self.assertIn("Claude Fable 5.2", statement)
        self.assertIn("GPT-6 Astra", statement)
        self.assertIn("Claude Haiku", statement)

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
            self.assertIn("Claude Fable 5.2", text)
            self.assertEqual(len(document.findall(".//w:tbl", ns)), 6)
            self.assertEqual(len(document.findall(".//w:drawing", ns)), 2)


if __name__ == "__main__":
    unittest.main()
