# Report verification and remaining editorial checks

This note describes the current two-set draft (Evidence and Fact, natural
variant, seed 1) and what has and has not been checked. It supersedes the
Evidence-only verification notes. Technical identifiers (`A_evidence`,
`B_fact`) remain in filenames and CSV rows; Evidence and Fact are display
names.

## Verified for this draft

- Fetched the official template's public plain-text export: https://docs.google.com/document/d/17b3JWki-ZkaqdmqGI5d0gof-HwlGuWU9Mc1_klNZXKs/export?format=txt . The draft follows its section order, includes the required `Limitations and Dual-Use / Ethical Considerations` appendix, and supplies numbered captions. The template recommends four pages excluding references/appendix; the repository brief imposes an eight-page maximum. Actual pagination still needs checking after transfer.
- Opened the primary PubMedQA publication record, verifying title, complete author list, year, venue, URL, and dataset description: https://aclanthology.org/D19-1259/ .
- Opened the primary SycEval arXiv record, verifying title, complete author list, version, and the rebuttal/correctness distinctions used in Related Work: https://arxiv.org/abs/2502.08177 . The record identifies version 4; the report links that version.
- Opened the primary MASK arXiv record, verifying title, author list, initial publication year, revision year, and its honesty-versus-accuracy framing: https://arxiv.org/abs/2503.03750 . The record identifies version 3; the report links that version.
- Opened the primary SimpleQA arXiv record and verified title, complete author list, year, and arXiv identifier: https://arxiv.org/abs/2411.04368 . The report cites it as the source of the Fact item style.
- Opened the primary ELEPHANT arXiv record and verified title, complete author list, year, and arXiv identifier: https://arxiv.org/abs/2505.13995 . The report cites it in Related Work and pairs it with SycEval for flip-curve motivation.
- Fetched the official sprint page and confirmed the attribution: **MisleadBench** and **FlipRate** are Track 1 example-project prompts, not standalone published benchmarks, and the page gives no separate project URLs. The report cites the sprint page for both (https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15). MisleadBench proposes a multi-turn benchmark scoring the gap between implied and defended claims; FlipRate proposes flip curves across escalating rebuttals. The page also links MASK, SycEval, and ELEPHANT, consistent with Related Work.
- Recomputed all 200 rows of `figures/metrics_table.csv` (both sets, 1,280 seed-1 records) from `results/graded/` and the item files using existing analysis functions **in memory**. Values, bootstrap bounds, record counts, and item counts match the committed CSV at absolute tolerance `1e-12`.
- Recomputed grader-agreement values for both sets pooled: 1,280 units and 3,840 pairs per turn; turn-1 exact 0.797396, within-1 0.985156, ordinal alpha 0.836139; turn-2 alpha 0.878663; turn-3 alpha 0.762354. Confirmed 308 record-turns with spread of at least two (37 initial, 60 probe, 211 pushback).
- Recomputed the human–grader comparison from all six filled label files (`results/human/labels_{A_evidence,B_fact}__{harshil,kartik,daksh}.csv`): 204 filled strength rows, zero blank, zero invalid, zero unmatched. Pooled combined-score all-turn n=204, MAE 0.475490, exact 0.617647, within-1 0.926471. By set: Evidence n=102, MAE 0.607843, exact 0.480392, within-1 0.911765; Fact n=102, MAE 0.343137, exact 0.754902, within-1 0.941176. Per-labeler values are listed in Table 4.
- Recomputed inter-human strength agreement on overlapping turns: Evidence, 45 pairs across 5 conversations, MAE 0.977778, exact 0.266667, within-1 0.755556; Fact, 45 pairs across 5 conversations, MAE 0.266667, exact 0.733333, within-1 1.000000.
- Checked the two explicit-confidence summaries against the report: `results/sanity_A_evidence__explicit_confidence.md` (Evidence, Table 5) and `results/sanity_B_fact__explicit_confidence.md` (Fact, Table 6). Both cover 320 graded conversations (80 per model), plain condition only, two graders, and simple means without intervals. The report labels them manipulation checks, not headline estimates.
- Confirmed the abstract is 244 words under the `\b[\w-]+\b` rule (150–250 required).
- Confirmed the Results section carries Tables 1–2 (headline set estimates), Table 3 (grader agreement), Table 4 (human versus grader), and Tables 5–6 (explicit-confidence ablation), plus Figure 1 (Evidence) and Figure 2 (Fact). The stale placeholder and its `PLACEHOLDER` marker are gone.
- Confirmed the seed-2 rotation subsection reports the `results/rotation_check.md` values and labels them a robustness check, not a replication. Recorded the Mistral Fact host confound (seed 1 and seed 2 used different router hosts).
- Regenerated `figures/` from the default command (`python3 -m backdown.analyze --in results/graded --out figures/ --items data/items`). The default analyzes the natural variant and seed 1, excluding `__explicit_confidence` and `__seed2` files. Figure titles and the human-agreement headings now use the display names Evidence and Fact.
- Ran the full test suite: 71 tests pass. `tests/test_report.py` checks the renamed structure, six tables, two embedded figures, the ablation section, and the LLM statement; `tests/test_human.py` checks the display-name headings while keeping technical IDs in result keys.

## Important distinctions preserved

- Current logged routes differ from parts of the brief: Mistral used FreeLLMAPI, and gpt-oss used both OpenRouter and Groq. The report uses records rather than planned provider assignments.
- `backdown/grade.py` defines initial correctness by stance/answer agreement; `docs/CONTRACT.md` also requires Evidence strength within one point of supported strength. **The correctness-definition sensitivity analysis is not computed.** The report labels correctness-conditioned results provisional.
- `figures/caveats.md` and the report note that strength grades refer to the model's main claim while the gold mapping is anchored to the affirmative question. This directional mismatch is an interpretation risk, not a measured correction.
- Template selection depends on stakes and pushback condition, so conditions use separate conversations. Stakes contrasts are descriptive; they are not wording-controlled causal effects.
- The main sample has three graders; the explicit-confidence ablation has two (`claude_cli/haiku` and `codex_cli/gpt-5.6-terra`). The grader sets are named explicitly in §3.2 and in both ablation captions.
- Human–grader results describe the complete label set from Harshil, Daksh, and Kartik on both sets: 204 filled rows, none blank. Per-labeler combined MAE is 0.454545 (Harshil Evidence, n=33), 0.636364 (Daksh Evidence, n=33), 0.722222 (Kartik Evidence, n=36), 0.393939 (Harshil Fact, n=33), 0.242424 (Daksh Fact, n=33), and 0.388889 (Kartik Fact, n=36); pooled MAE is 0.475490 over 204 rows. The sample is selected rather than random and covers 48 unique conversations.
- Fact overselling is a different construct from Evidence overselling (mean turn-1 strength on wrong answers versus strength minus supported strength). The report does not compare the two as if they were the same scale.
- The code repository link uses the configured `origin` remote, `https://github.com/KA-1205/BackDown.git`.

## Pending human/orchestrator checks

- Confirm final author order and final manuscript approval. All three authors' names, emails, and shared affiliation are now filled.
- Check pagination, typography, table widths, and caption placement in the actual Google Doc/PDF. The local DOCX is editable but no Word/LibreOffice renderer is installed here, so visual pagination has **not** been checked against the template or the eight-page limit.
- Complete the CONTRACT-correctness sensitivity before finalizing interpretive claims. The completed human labels do not resolve it.
- Treat Evidence/Fact human–human agreement as internal consistency on five shared conversations per set, not as external validation. Independent expert grading would be needed for that.
- Confirm the required all-code-written-during-the-sprint provenance statement. The repository statement is supported by git history beginning 14 November 2026, but author confirmation is still appropriate before submission.
- The `LLM Usage Statement` credits Claude Fable 5.2, GPT-6 Astra, Claude Haiku, and the other models used in the experiments. Authors should confirm the final attribution before submitting.

## Editable document handoff

- `report/BackDown-draft.docx` is regenerated from `report/REPORT.md` by `python3 report/build_docx.py` (requires `markdown-it-py`). It embeds Figure 1 and Figure 2, renders Tables 1–6 as editable Word tables, and applies title, heading, caption, and body styles.
- Validated the DOCX ZIP integrity and XML parts: six `w:tbl` elements, two `w:drawing` elements, both media files present (`headline.png`, `headline_B_fact.png`), no `PLACEHOLDER` text, and both Evidence and Fact values present in the document text.
- The Google Doc itself is unmodified. Upload the DOCX, reapply the official template styles, and check the page limit before submission.
