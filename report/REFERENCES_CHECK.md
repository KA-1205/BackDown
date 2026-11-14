# Report verification and remaining editorial checks

## Verified for this draft

- Fetched the official template's public plain-text export: https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/export?format=txt . The draft follows its section order, includes the required ethics appendix, and supplies numbered captions. The template recommends four pages excluding references/appendix; the repository brief imposes an eight-page maximum. Actual pagination still needs checking after transfer.
- Opened the primary PubMedQA publication record, verifying title, complete author list, year, venue, URL, and dataset description: https://aclanthology.org/D19-1259/ .
- Opened the primary SycEval arXiv record, verifying title, complete author list, version, and the rebuttal/correctness distinctions used in Related Work: https://arxiv.org/abs/2502.08177 . The record identifies version 4; the report links that version.
- Opened the primary MASK arXiv record, verifying title, author list, initial publication year, revision year, and its honesty-versus-accuracy framing: https://arxiv.org/abs/2503.03750 . The record identifies version 3; the report links that version. Its authors are Richard Ren, Arunim Agarwal, Mantas Mazeika, Cristina Menghini, Robert Vacareanu, Brad Kenstler, Mick Yang, Isabelle Barrass, Alice Gatti, Xuwang Yin, Eduardo Trevino, Matias Geralnik, Adam Khoja, Dean Lee, Summer Yue, and Dan Hendrycks.
- Recomputed all 100 rows of `figures/metrics_table.csv`, including values, bootstrap interval bounds, record counts, and item counts, from `results/graded/` and `data/items/A_evidence.jsonl` using existing analysis functions **in memory**. All matched at absolute tolerance `1e-12`. Python bytecode writes were disabled; no figures or analysis files were regenerated.
- Recomputed grader-agreement values and the 132 spread-at-least-two units. Checked item label distribution, complete grader coverage, logged model/provider identities, condition counts, seed, error/duplicate counts, and truncation totals directly from source records. Viewed `figures/headline.png`.
- Checked the updated report's abstract length (222 whitespace-delimited words, within 150–250) and exact type-B subsection content. For this update, author Kartik's final human labels were read for the comparison: 36 filled strength rows across 12 conversations, with all three turns labeled. The other two labeler files each retain 33 blank strength rows (66 total).
- Matched Table 3 to the regenerated `figures/grader_agreement.md`: combined all-turn n=36, MAE 0.722222, exact agreement 0.361111, within-one agreement 0.916667; per-turn n=12 and estimates are reproduced from its `combined` rows. The artifact reports zero invalid strengths and zero unmatched conversation/turn identifiers. This update uses the orchestrator's regenerated comparison; the earlier full-result recomputations above describe the original draft checks.
- Confirmed sequential Table 1–3 and Figure 1 captions and the Results 4.4 `PENDING` marker. Before/after hashes confirm the original Results 4.1–4.3 (including both original tables and the figure caption), author metadata, citations, TODOs, generator, headline image, and regenerated agreement source were preserved.

## Important distinctions preserved

- Current logged routes differ from parts of the brief: Mistral used FreeLLMAPI, and gpt-oss used both OpenRouter and Groq. The report uses records rather than planned provider assignments.
- `backdown/grade.py` defines correctness by stance/label agreement; `docs/CONTRACT.md` also requires strength within one point of supported strength. The sensitivity analysis is not computed.
- `figures/caveats.md` describes correctness ties as “not correct,” but current `_majority` returns `None` on ties. The report follows the implementation's unknown/excluded behavior. This does not alter the reproduced snapshot metrics.
- Strength grades refer to the model's main claim; the gold mapping is anchored to the affirmative question. The report identifies this directional mismatch as an interpretation risk, not a measured correction to the published scores.
- Template selection depends on stakes and pushback condition. Stakes contrasts are descriptive; changing conditions is not a wording-controlled intervention.
- Human–grader strength findings now describe Kartik's completed labels only. This is a small convenience/stratified selected sample with repeated turns and overlapping author assignments, not completed independent multi-human or unbiased general validation. Further human grading is pending; no inter-human agreement estimate is available.
- Corrected the code repository link to the configured `origin` remote, `https://github.com/KA-1205/BackDown.git`; the initial draft linked a different owner.

## Pending human/orchestrator checks

- Confirm full author names, author order, affiliations, and final manuscript approval.
- Verify the sprint-page MisleadBench/FlipRate attribution and primary URL. Web search was unavailable (HTTP 402); the draft explicitly marks this citation TODO rather than presenting it as externally verified.
- Confirm the required all-code-written-during-the-sprint provenance statement. The project brief requests this assertion, but it was not independently established.
- Complete further independent human grading and correctness-definition sensitivity before finalizing interpretive claims; Kartik's 36 completed strength labels do not resolve these checks.
- Check pagination, typography, and caption placement in the actual Google Doc/PDF. This update edited local report Markdown and regenerated the editable DOCX.
- The existing `tests/test_report_placeholder.py` scaffold check was not modified. Results 4.4 retains a visible `PENDING` marker for additional human labeling and adds Table 3 with Kartik's available comparison; the orchestrator is updating the stale no-table expectation while preserving the type-B placeholder constraints.
- Drafting used this session's GPT-6 Astra identity. The requested “high” reasoning variant is not independently inspectable through the available session tools.

## Editable document handoff

- `report/BackDown-draft.docx` is an editable Word file regenerated from `report/REPORT.md` by `python3 report/build_docx.py` (requires `markdown-it-py`, available in the drafting environment). It embeds Figure 1, renders Tables 1–3 as editable Word tables, and applies title, heading, caption, and body styles. It can be uploaded to Google Docs for final editing.
- Validated the regenerated DOCX ZIP integrity and XML parts; confirmed three editable tables, Table 3 values matching the Markdown, the additional-labeling `PENDING` marker, and one embedded figure identical to `figures/headline.png`.
- The Google Doc is not modified. No Word/LibreOffice renderer is installed here, so actual pagination, line wrapping, and caption placement have **not** been visually checked. Check the uploaded document against the template and the eight-page limit before submission.
