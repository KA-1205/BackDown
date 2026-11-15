# Report verification and remaining editorial checks

This note describes the current two-type draft (type A and type B, seed 1) and
what has and has not been checked. It supersedes the type-A-only verification
notes.

## Verified for this draft

- Fetched the official template's public plain-text export: https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/export?format=txt . The draft follows its section order, includes the required `Limitations and Dual-Use / Ethical Considerations` appendix, and supplies numbered captions. The template recommends four pages excluding references/appendix; the repository brief imposes an eight-page maximum. Actual pagination still needs checking after transfer.
- Opened the primary PubMedQA publication record, verifying title, complete author list, year, venue, URL, and dataset description: https://aclanthology.org/D19-1259/ .
- Opened the primary SycEval arXiv record, verifying title, complete author list, version, and the rebuttal/correctness distinctions used in Related Work: https://arxiv.org/abs/2502.08177 . The record identifies version 4; the report links that version.
- Opened the primary MASK arXiv record, verifying title, author list, initial publication year, revision year, and its honesty-versus-accuracy framing: https://arxiv.org/abs/2503.03750 . The record identifies version 3; the report links that version.
- Opened the primary SimpleQA arXiv record and verified title, complete author list, year, and arXiv identifier: https://arxiv.org/abs/2411.04368 . The report cites it as the source of the type-B item style.
- Opened the primary ELEPHANT arXiv record and verified title, complete author list, year, and arXiv identifier: https://arxiv.org/abs/2505.13995 . The report cites it in Related Work and pairs it with SycEval for flip-curve motivation.
- Fetched the official sprint page and confirmed it names **MisleadBench** and **FlipRate** as the Track 1 example projects cited in the Introduction: https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15 . The page also links MASK, SycEval, and ELEPHANT, consistent with Related Work.
- Recomputed all 200 rows of `figures/metrics_table.csv` (both types, 1,280 seed-1 records) from `results/graded/` and the item files using existing analysis functions **in memory**. Values, bootstrap bounds, record counts, and item counts match the committed CSV at absolute tolerance `1e-12`.
- Recomputed grader-agreement values for both types pooled: 1,280 units and 3,840 pairs per turn; turn-1 exact 0.797396, within-1 0.985156, ordinal alpha 0.836139; turn-2 alpha 0.878663; turn-3 alpha 0.762354. Confirmed 308 record-turns with spread of at least two (37 initial, 60 probe, 211 pushback).
- Recomputed the human–grader comparison from `results/human/labels_A_evidence__kartik.csv`: 36 filled strength rows over 12 conversations and three turns, zero invalid, zero unmatched. Combined-score rows: all turns n=36, MAE 0.722222, exact 0.361111, within-1 0.916667; per-turn n=12 matching Table 4.
- Confirmed the abstract is 225 words under the `\b[\w-]+\b` rule (150–250 required).
- Confirmed the Results section carries Table 1 (type A), Table 2 (type B), Table 3 (grader agreement), and Table 4 (human vs grader), plus Figure 1 (type A) and Figure 2 (type B). The stale type-B placeholder and its `PLACEHOLDER` marker are gone.
- Confirmed the seed-2 rotation subsection reports the `results/rotation_check.md` values and labels them a robustness check, not a replication. Recorded the Mistral type-B host confound (seed 1 and seed 2 used different router hosts).
- Regenerated `figures/` from the default command (`python3 -m backdown.analyze --in results/graded --out figures/`). The default now analyzes the natural variant and seed 1, excluding `__explicit_confidence` and `__seed2` files. `figures/headline.png` was byte-identical to the prior type-A figure; `figures/headline_B_fact.png` is new.
- Ran the full test suite: 66 tests pass. The report test was renamed from `tests/test_report_placeholder.py` to `tests/test_report.py` and now checks the two-type structure, four tables, two embedded figures, and the pending-validation language.

## Important distinctions preserved

- Current logged routes differ from parts of the brief: Mistral used FreeLLMAPI, and gpt-oss used both OpenRouter and Groq. The report uses records rather than planned provider assignments.
- `backdown/grade.py` defines initial correctness by stance/answer agreement; `docs/CONTRACT.md` also requires type-A strength within one point of supported strength. **The correctness-definition sensitivity analysis is not computed.** The report labels correctness-conditioned results provisional.
- `figures/caveats.md` and the report note that strength grades refer to the model's main claim while the gold mapping is anchored to the affirmative question. This directional mismatch is an interpretation risk, not a measured correction.
- Template selection depends on stakes and pushback condition, so conditions use separate conversations. Stakes contrasts are descriptive; they are not wording-controlled causal effects.
- Human–grader results describe Kartik's completed type-A labels only: a small selected sample with repeated turns within 12 conversations, not independent multi-human validation. **168 strength rows remain blank** across the other five label files (type-A Harshil and Daksh, and all three type-B files). No human labels cover type B.
- Type-B overselling is a different construct from type-A overselling (mean turn-1 strength on wrong answers versus strength minus supported strength). The report does not compare the two as if they were the same scale.
- The code repository link uses the configured `origin` remote, `https://github.com/KA-1205/BackDown.git`.

## Pending human/orchestrator checks

- Confirm final author order and Harshil's and Daksh's affiliations; Kartik's name, email, and affiliation are now filled. Final manuscript approval also remains.
- Check pagination, typography, table widths, and caption placement in the actual Google Doc/PDF. The local DOCX is editable but no Word/LibreOffice renderer is installed here, so visual pagination has **not** been checked against the template or the eight-page limit.
- Complete further independent human grading and the CONTRACT-correctness sensitivity before finalizing interpretive claims. Kartik's 36 labels do not resolve either.
- Add human labels for type B before making any type-B human-validation claim.
- Confirm the required all-code-written-during-the-sprint provenance statement. The repository statement is supported by git history beginning 14 November 2026, but author confirmation is still appropriate before submission.
- The report-drafting request named GPT-6 Astra (high) through a subagent dispatch; the provider returned HTTP 400, so the revision was completed in the orchestrating session. The `LLM Usage Statement` credits GPT-6 Astra with drafting and checking; authors should confirm that attribution before submitting.

## Editable document handoff

- `report/BackDown-draft.docx` is regenerated from `report/REPORT.md` by `python3 report/build_docx.py` (requires `markdown-it-py`). It embeds Figure 1 and Figure 2, renders Tables 1–4 as editable Word tables, and applies title, heading, caption, and body styles.
- Validated the DOCX ZIP integrity and XML parts: four `w:tbl` elements, two `w:drawing` elements, both media files present (`headline.png`, `headline_B_fact.png`), no `PLACEHOLDER` text, and both type-A and type-B values present in the document text.
- The Google Doc itself is unmodified. Upload the DOCX, reapply the official template styles, and check the page limit before submission.
