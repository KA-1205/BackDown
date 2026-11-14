# Report verification and remaining editorial checks

## Verified for this draft

- Fetched the official template's public plain-text export: https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/export?format=txt . The draft follows its section order, includes the required ethics appendix, and supplies numbered captions. The template recommends four pages excluding references/appendix; the repository brief imposes an eight-page maximum. Actual pagination still needs checking after transfer.
- Opened the primary PubMedQA publication record, verifying title, complete author list, year, venue, URL, and dataset description: https://aclanthology.org/D19-1259/ .
- Opened the primary SycEval arXiv record, verifying title, complete author list, version, and the rebuttal/correctness distinctions used in Related Work: https://arxiv.org/abs/2502.08177 . The record identifies version 4; the report links that version.
- Opened the primary MASK arXiv record, verifying title, author list, initial publication year, revision year, and its honesty-versus-accuracy framing: https://arxiv.org/abs/2503.03750 . The record identifies version 3; the report links that version. Its authors are Richard Ren, Arunim Agarwal, Mantas Mazeika, Cristina Menghini, Robert Vacareanu, Brad Kenstler, Mick Yang, Isabelle Barrass, Alice Gatti, Xuwang Yin, Eduardo Trevino, Matias Geralnik, Adam Khoja, Dean Lee, Summer Yue, and Dan Hendrycks.
- Recomputed all 100 rows of `figures/metrics_table.csv`, including values, bootstrap interval bounds, record counts, and item counts, from `results/graded/` and `data/items/A_evidence.jsonl` using existing analysis functions **in memory**. All matched at absolute tolerance `1e-12`. Python bytecode writes were disabled; no figures or analysis files were regenerated.
- Recomputed grader-agreement values and the 132 spread-at-least-two units. Checked item label distribution, complete grader coverage, logged model/provider identities, condition counts, seed, error/duplicate counts, and truncation totals directly from source records. Viewed `figures/headline.png`.
- Checked the report's abstract length and exact type-B subsection content. No partial human labels were read or used.

## Important distinctions preserved

- Current logged routes differ from parts of the brief: Mistral used FreeLLMAPI, and gpt-oss used both OpenRouter and Groq. The report uses records rather than planned provider assignments.
- `backdown/grade.py` defines correctness by stance/label agreement; `docs/CONTRACT.md` also requires strength within one point of supported strength. The sensitivity analysis is not computed.
- `figures/caveats.md` describes correctness ties as “not correct,” but current `_majority` returns `None` on ties. The report follows the implementation's unknown/excluded behavior. This does not alter the reproduced snapshot metrics.
- Strength grades refer to the model's main claim; the gold mapping is anchored to the affirmative question. The report identifies this directional mismatch as an interpretation risk, not a measured correction to the published scores.
- Template selection depends on stakes and pushback condition. Stakes contrasts are descriptive; changing conditions is not a wording-controlled intervention.
- Human-vs-grader findings remain pending regardless of the older artifact's “No human labels yet” wording.
- Corrected the code repository link to the configured `origin` remote, `https://github.com/KA-1205/BackDown.git`; the initial draft linked a different owner.

## Pending human/orchestrator checks

- Confirm full author names, author order, affiliations, and final manuscript approval.
- Verify the sprint-page MisleadBench/FlipRate attribution and primary URL. Web search was unavailable (HTTP 402); the draft explicitly marks this citation TODO rather than presenting it as externally verified.
- Confirm the required all-code-written-during-the-sprint provenance statement. The project brief requests this assertion, but it was not independently established.
- Complete human validation and correctness-definition sensitivity before finalizing interpretive claims.
- Check pagination, typography, and caption placement in the actual Google Doc/PDF. This work edited local Markdown only.
- The known headings-only `tests/test_report_placeholder.py` scaffold check was not run or modified; the orchestrator must replace it for the drafted report.
- Drafting used this session's GPT-6 Astra identity. The requested “high” reasoning variant is not independently inspectable through the available session tools.

## Editable document handoff

- `report/BackDown-draft.docx` is an editable Word file generated from `report/REPORT.md` by `python3 report/build_docx.py` (requires `markdown-it-py`, available in the drafting environment). It embeds Figure 1, renders the two tables as editable Word tables, and applies title, heading, caption, and body styles. It can be uploaded to Google Docs for final editing.
- The Google Doc is not modified. No Word/LibreOffice renderer is installed here, so actual pagination, line wrapping, and caption placement have **not** been visually checked. Check the uploaded document against the template and the eight-page limit before submission.
