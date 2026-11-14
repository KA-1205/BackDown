# Implementation Plan: BackDown analysis pipeline (P0)

**Method:** incremental implementation — implement → test → verify → commit → next slice
**Source:** `KARTIK.md` §2, `docs/SPEC.md` §6 and §9, `docs/CONTRACT.md` §3–5
**Status:** awaiting human approval (no implementation started)
**Owner:** GPT-6 Astra (medium) implements; BigPickle orchestrates, verifies, commits.

## Overview

Build the missing analysis pipeline that turns the **640 graded type-A conversations** into the report's metrics, confidence intervals, inter-grader reliability, and headline figure. Also build a contract-compliant fake-data generator so each slice can be verified before/without real data.

No spec sheet and no test-first discipline. Each slice is the smallest complete piece that leaves `python -m backdown.analyze` working, is verified on fixtures, and is committed before the next slice.

**Non-goal for this plan:** human label collection, chat-app study, report prose, and type-B data collection. These appear in Phase 5 as a roadmap only.

## Scope

**In scope**
- `scripts/make_fake_graded.py` → `tests/fixtures/` (gitignored)
- `backdown/analyze.py` and its CLI
- `tests/test_*.py` (stdlib `unittest`)
- `figures/` outputs

**Out of scope**
- Any edit to `results/`, `data/`, `templates/`, `config/`, `docs/CONTRACT.md`
- Any change to `backdown/run.py`, `grade.py`, `clients.py`, `io.py`, `config.py`
- Filling `results/human/labels_*.csv`
- Inventing type-B data or filling missing graders

## Assumptions (correct me now or I proceed)

1. **Real-data target is type A only.** Type B is absent; the code degrades gracefully and never fabricates.
   - **Type B in the report is a structural placeholder only.** It gets a heading, a one-line statement that results are pending, and a note on what will go there (same metrics, same four models). It contains **no numbers, no claims, and no attribution** — it must not name who will deliver the data or imply results already exist. `analyze.py` prints `type B: no data (blocked)` rather than omitting the type silently.
2. **Grader combination:** final strength per turn = median of the graders present. Missing grader = missing, never zero.
3. **Correctness:** use the grader-reported `correct` field (stance match for A, answer match for B), combined by majority. Ties count as not-correct for correct-only subsets.
   - Known inconsistency: `docs/CONTRACT.md` §4 says type-A correctness is "strength within 1 point + direction matches", but `backdown/grade.py` asks graders only for stance match. Primary uses what the data logs; a strength-within-1 sensitivity metric is also emitted.
4. **Oversold (type A):** median turn-1 strength > `gold.supported_strength`.
5. **Discrimination:** within each pushback condition, mean retreat on that condition's wrong/oversold turn-1 records; then `warranted − unwarranted`. Independent subsets (not item-paired); a paired sensitivity variant is included.
6. **Headline x-axis:** overselling pooled across both pushback conditions; y-axis: discrimination. One plain and one stakes point per model, arrow plain → stakes.
7. **Bootstrap:** cluster by `item_id`, 1,000 resamples, fixed seed `12345`, 95% percentile CI.
8. **Human labels:** comparison is implemented; it reports "no labels yet" until humans fill them. Agents never fill labels.
9. **Dependencies:** increments 1–6 use only the Python stdlib (`json`, `csv`, `statistics`, `random`, `unittest`). Increment 7 needs `matplotlib` only.
10. **Outputs:** the analysis writes only under `--out` (default `figures/`). It never writes to `results/`.

## Architecture decisions

- **Stdlib-first.** `json`/`csv`/`statistics`/`random` cover loading, medians, bootstrap, and tables. Avoid pandas/numpy until a real need appears. `matplotlib` is imported only inside the figure function.
- **Pure metric functions** (combined records in → numbers out) so each slice is verifiable without I/O.
- **Thin loader** separate from computation; dedupe by `conv_id` (latest line wins), skip `error` records and count them.
- **One module** `backdown/analyze.py`; tests import functions directly.
- **Long-format metrics table** (`type, model, stakes, pushback, metric, value, ci_low, ci_high, n, n_items`), introduced in Increment 2 and extended each slice.
- **Determinism:** sorted file/model keys, fixed bootstrap seed, no unordered set iteration in outputs.
- **Figure is B&W-safe:** distinct markers + linestyles + direct text labels, not colour alone.
- **Truncation flag:** carry `finish_reason == "length"` from `turn_meta` so truncated turns (gpt_oss 19, nemotron 9 in type A) can be reported.

## Dependency graph

```
Increment 1  fixtures + loader + CLI skeleton
     └── Increment 2  combine scores + overselling + table
           ├── Increment 3  probe retreat + capitulation + stakes effect
           └── Increment 4  discrimination
                 └── Increment 5  bootstrap CIs
                       └── Increment 6  grader agreement + human comparison
                             └── Increment 7  full tables + headline figure (matplotlib)
                                   └── Increment 8  real-data run + hand-off
                                         └── Increment 9  report scaffold + type-B placeholder
```

## Increment 1 — Fixtures, loader, CLI skeleton

**Goal:** `python -m backdown.analyze --in <dir> --out <dir>` loads graded JSONL, dedupes, skips errors, and prints a summary. A fixture generator produces contract-compliant test data.

**Implement**
- `scripts/make_fake_graded.py`: 2 types × 4 models × 2 stakes × 2 pushbacks × 3 graders, deterministic, writes `tests/fixtures/` only.
- `backdown/analyze.py`: `load_graded()`, `main()` with `--in`/`--out`, counts by type/model/condition.

**Test**
- `tests/test_loader.py`: dedupe by `conv_id`, skip `error`, empty dir, malformed line policy.
- `tests/test_fixtures.py`: required fields, balanced conditions, 3 graders.

**Verify**
- Generate fixtures; run CLI on fixtures and on `results/graded/`.
- Real-data summary must report **640 records, 4 models × 160, 3 graders, 4 conditions × 160**.

**Commit:** `Analyze: add loader, CLI skeleton, and fixtures`

**Size:** M · **Files:** `backdown/analyze.py`, `scripts/make_fake_graded.py`, `tests/test_loader.py`, `tests/test_fixtures.py`, `tests/fixtures/` (gitignored)

## Increment 2 — Score combination + overselling

**Goal:** first real metric end-to-end: median strengths, majority correctness, and overselling rows in the table.

**Implement**
- `combine_grades(record)`: median strength per turn, majority `correct` / `changed_answer`, missing-grader flags.
- `overselling(records)`: type A = mean(turn1 − `gold.supported_strength`); type B = mean turn-1 strength on wrong answers.
- `write_metrics_table()` with the overselling rows only.

**Test**
- `tests/test_combine.py`: 1/2/3 graders, missing grader, correctness tie.
- `tests/test_metrics.py`: hand-computed overselling on a toy fixture.

**Verify**
- Fixture value matches by hand.
- Real-data overselling is in the expected range (~+1.3 to +1.9) and the table has one row per model × stakes × pushback.

**Commit:** `Analyze: combine grader scores and add overselling`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_combine.py`, `tests/test_metrics.py`, `figures/metrics_table.csv`

## Increment 3 — Probe retreat, capitulation, stakes effect

**Goal:** the remaining non-discrimination metrics, all in the table.

**Implement**
- `probe_retreat(records)` = mean(turn1 − turn2).
- `capitulation(records)` = share of correct turn-1, unwarranted records with `changed_answer`.
- `stakes_effect(metric)` = stakes − plain, paired by item where required.

**Test**
- Hand-computed tiny cases; empty subsets return missing with `n=0`; zero correct records returns missing, not 0.

**Verify**
- Real-data probe retreat and capitulation match the ad-hoc estimates (± rounding).
- Stakes effect appears for every metric that has both conditions.

**Commit:** `Analyze: add probe retreat, capitulation, and stakes effect`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_metrics.py`

## Increment 4 — Discrimination

**Goal:** the headline-risk metric, with a paired sensitivity check.

**Implement**
- `discrimination(records)`: warranted retreat − unwarranted retreat, each on its own wrong/oversold turn-1 records.
- Pair by `item_id` in a sensitivity variant.

**Test**
- 2-item toy set with a known positive and negative discrimination.
- Empty subset returns missing, `n=0`.

**Verify**
- Real-data values reproduce the ad-hoc estimates (all negative, ~−0.6 to −1.2 plain).
- Paired vs independent differ by a documented amount.

**Commit:** `Analyze: add discrimination and paired sensitivity`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_metrics.py`

## Increment 5 — Bootstrap confidence intervals

**Goal:** 95% cluster-bootstrap CIs for every metric.

**Implement**
- `bootstrap_ci(records, metric_fn, n=1000, seed=12345)`: resample `item_id`s with replacement; percentile CI.
- Attach CIs to all table rows.

**Test**
- Two runs are identical.
- CI brackets the point estimate on fixtures.
- `n=1` returns a degenerate CI without crashing.
- Paired metrics resample items, not records.

**Verify**
- Real-data table has `ci_low`/`ci_high` for every row; no NaNs.

**Commit:** `Analyze: add item-level bootstrap confidence intervals`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_bootstrap.py`

## Increment 6 — Grader agreement + human comparison

**Goal:** reliability reporting and the human-vs-grader hook.

**Implement**
- Pairwise exact / within-1 agreement per turn.
- Krippendorff's alpha (ordinal) per turn.
- Disagreement list (`conv_id`, turn, grader values) for spread ≥ 2.
- Human-vs-grader MAE / exact / within-1 from `results/human/labels_*.csv`; empty-safe.
- Write `figures/grader_agreement.md` and `figures/grader_disagreements.csv`.

**Test**
- Perfect-agreement fixture → alpha = 1.0.
- Known-disagreement fixture → expected alpha < 1.
- Units with < 2 graders skipped.
- Empty human labels → "no labels yet", no crash.

**Verify**
- Alpha on real data is near the ad-hoc estimate (~0.56 / 0.76 / 0.76).
- Disagreement count is reported (110/1,920 turns at spread ≥ 2 in the earlier audit).

**Commit:** `Analyze: add grader agreement and human comparison`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_agreement.py`, `tests/test_human.py`, `figures/grader_agreement.md`, `figures/grader_disagreements.csv`

## Increment 7 — Tables and headline figure

**Goal:** the report-ready outputs.

**Implement**
- Finish `figures/metrics_table.csv` and `.md` (all metrics, NA not nan).
- `figures/headline.png`: x = overselling (pooled pushbacks), y = discrimination, plain + stakes point per model, bootstrap error bars, arrow plain → stakes, direct labels, B&W-safe.

**Test**
- Table schema/row-count test.
- Figure smoke test: file exists and is > 20 KB.

**Verify**
- Human visually reviews the figure in greyscale.
- All four required outputs exist.

**Dependency:** `sudo apt-get install -y python3-matplotlib` (or a venv with matplotlib).

**Commit:** `Analyze: produce metrics tables and headline figure`

**Size:** M · **Files:** `backdown/analyze.py`, `tests/test_tables.py`, `tests/test_figure.py`, `figures/*`

## Increment 8 — Real-data run and hand-off

**Goal:** run on the 640 real records, capture headline numbers and caveats.

**Implement:** bug fixes only; no new features.

**Verify**
- `python -m backdown.analyze --in results/graded --out figures/` exits 0.
- Second run reproduces identical numbers.
- All outputs exist; `git status` shows only allowed files.
- Caveats documented: negative discrimination, correctness-definition sensitivity, truncated turns, type-B absent.

**Commit:** `Analyze: run on real type-A data`

**Size:** S · **Files:** `figures/*` only

## Increment 9 — Report scaffold + type-B placeholder

**Goal:** reserve the type-B section of the report so it cannot be quietly filled with invented numbers later, without claiming any result exists.

**Implement**
- `report/` scaffold (headings only): Abstract, Introduction, Related Work, Methodology, Results (A + B), Discussion, Limitations, Dual-Use appendix.
- `report/type_b_placeholder.md` (or the B subsection of Results) containing exactly:
  - a heading for the type-B results;
  - one sentence: results are pending and this section will report the same metrics for the same four models;
  - a short bullet list of the metrics that will appear, each marked `pending`;
  - a visible `> PLACEHOLDER — no type-B data exists in this repository yet` marker.
- No numbers, no estimated values, no person named as the source, no citation, no "preliminary" findings.

**Test**
- `tests/test_report_placeholder.py`: asserts the file exists, contains the placeholder marker, contains no digits that look like results, and names no person.

**Verify**
- Read the rendered section; confirm it cannot be mistaken for a result.
- Confirm `analyze.py` summary prints type B as blocked/no-data.

**Dependency:** none for the placeholder; the Results-A part waits on Increment 8.

**Commit:** `Report: scaffold and neutral type-B placeholder`

**Size:** S · **Files:** `report/*`, `tests/test_report_placeholder.py`

## Checkpoints

- **After Inc 1:** CLI counts match (640, 4×160, 3 graders, 4×160 conditions).
- **After Inc 2:** overselling hand-checked on a toy fixture and sane on real data.
- **After Inc 4:** all core metrics hand-checked; definitions reviewed by human.
- **After Inc 5:** CIs deterministic; table has no NaNs.
- **After Inc 6:** alpha sanity-checked; empty human labels handled.
- **After Inc 7:** figure reviewed; all required outputs present.
- **After Inc 8:** P0 definition of done met; commit + push.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Correctness definition mismatch (`CONTRACT` vs `grade.py`) | Med — changes capitulation/subset sizes | Primary uses logged `correct`; strength-within-1 sensitivity; flag in report |
| Negative discrimination is a wording artifact | High — headline interpretation | Report definition, paired sensitivity, and the "conclusion may agree" caveat |
| Type B absent | Med — two-type comparison impossible | Generic code + explicit blocked handling; never fabricate |
| Truncated turns (gpt_oss 19, nemotron 9) | Med — biased strengths | Flag `finish_reason=length`; report count |
| Only 40 items → wide CIs | Med | Cluster bootstrap; report CIs honestly |
| Grader noise (α ≈ 0.56 on turn 1) | Med | Report α and disagreement list; median reduces variance |
| Human labels empty | Med — validation section empty | Human-only task; comparison ready to run |
| Scope creep into report/chat-app | Med | This plan is P0 only; Phase 5 is roadmap |
| Matplotlib missing | Med — blocks Inc 7 only | Install before Inc 7; Incs 1–6 are stdlib-only |

## Phase 5 — Non-code roadmap (not this plan)

| Task | Owner | Dependency | Status |
|---|---|---|---|
| Fill 36 blind type-A labels (12 conversations) | Humans | none | ready, human-only |
| Human-vs-grader report section | Kartik/Astra | labels filled | blocked on labels |
| `docs/chat_app_study.md` protocol | Kartik/Astra | none | ready |
| ~7 chat-app conversations each; collate `results/chat_app/` | Harshil/Daksh/Kartik | protocol | ready |
| Report Intro, Related Work, Methodology, Limitations appendix | Astra drafts, Kartik reviews | none | ready |
| Report Results/Discussion/Abstract | Astra drafts, Kartik reviews | P0 outputs | blocked on P0 |
| Type-B pipeline + results | Daksh | SimpleQA items | blocked on Daksh |

## Open questions (defaults chosen; confirm or override)

1. **Scope:** this plan is the P0 analysis pipeline; Phase 5 is roadmap-only. Default: confirm.
2. **Correctness:** primary = logged grader `correct`; sensitivity = `CONTRACT` strength-within-1. Default: do both.
3. **Discrimination:** independent per-pushback subsets + paired sensitivity. Default: do both.
4. **Headline x-axis:** pool both pushbacks. Default: pool.
5. **Tests:** stdlib `unittest`, not pytest. Default: yes.
6. **Touch set:** add `tests/test_*.py` and `tasks/` to the `rules.md` file-boundary table. Default: update in Increment 1.
7. **Pushed commit `5e10283`:** author email is `.125`; rewrite with `.1205` (force-push, needs explicit OK) or leave it? Pending.
8. **Start now?** Increment 1 needs no installs. Default: start on approval.
