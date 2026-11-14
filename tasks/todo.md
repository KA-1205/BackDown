# P0 task list — BackDown analysis pipeline

Plan: `tasks/plan.md` · Method: incremental (implement → test → verify → commit)
Owner: GPT-6 Astra (implement) / BigPickle (orchestration, git, verification)

## Status snapshot (verified 2026-11-14)
- Type A: **complete** — 640 raw + 640 graded, 4 models × 160, 3 graders × 640, 4 conditions × 160.
- Type B: **absent** — no items, no templates, no raw, no graded. Blocked; placeholder only.
- Human labels: 24 type-A conversations sampled at seed 7; **all label rows empty** (human-only).
- `backdown/analyze.py`: **does not exist** — this is P0.

## Increment 1 — Fixtures, loader, CLI skeleton
- [x] `scripts/make_fake_graded.py` (deterministic, contract-compliant, writes `tests/fixtures/` only)
- [x] `backdown/analyze.py`: `load_graded()` + `main()` with `--in` / `--out`
- [x] `tests/test_loader.py`, `tests/test_fixtures.py` (stdlib `unittest`)
- [x] Verify on real data: 640 records, 4 models × 160, 3 graders, 4 conditions × 160
- [x] Commit + push (`93342a3`)

## Increment 2 — Score combination + overselling
- [x] `combine_grades()`: median strength, majority `correct` / `changed_answer`, missing ≠ zero
- [x] `overselling()`: type A vs `gold.supported_strength`; type B path reports no-data
- [x] Metrics table (long format) with overselling rows
- [x] `tests/test_combine.py`, `tests/test_metrics.py`
- [x] Independently recomputed all 24 rows from raw JSONL — exact match
- [x] Commit + push

## Increment 3 — Probe retreat, capitulation, stakes effect
- [ ] `probe_retreat()` = mean(turn1 − turn2)
- [ ] `capitulation()` = changed share of correct turn-1 on unwarranted pushback
- [ ] `stakes_effect()` = stakes − plain
- [ ] Tests: empty subset → missing + `n=0`; no correct records → missing, not 0
- [ ] Commit + push

## Increment 4 — Discrimination
- [ ] warranted retreat − unwarranted retreat on wrong/oversold turn-1
- [ ] paired-by-item sensitivity variant
- [ ] `tests/test_metrics.py` toy set with known sign
- [ ] Commit + push

## Increment 5 — Bootstrap CIs
- [ ] item-level cluster bootstrap, 1,000 resamples, seed `12345`, 95% percentile
- [ ] CIs attached to every table row; `n=1` degenerate but no crash
- [ ] `tests/test_bootstrap.py` (seed-repeat determinism)
- [ ] Commit + push

## Increment 6 — Grader agreement + human comparison
- [ ] pairwise exact / within-1, Krippendorff ordinal α per turn
- [ ] disagreement list (spread ≥ 2) → `figures/grader_disagreements.csv`
- [ ] human-vs-grader MAE / exact / within-1, empty-safe
- [ ] `figures/grader_agreement.md`
- [ ] `tests/test_agreement.py`, `tests/test_human.py`
- [ ] Commit + push

## Increment 7 — Tables and headline figure (needs matplotlib)
- [ ] `figures/metrics_table.csv` + `.md`, NA not nan
- [ ] `figures/headline.png`: x = overselling (pooled pushbacks), y = discrimination, plain→stakes arrow, B&W-safe
- [ ] `tests/test_tables.py`, `tests/test_figure.py`
- [ ] Commit + push

## Increment 8 — Real-data run and hand-off
- [ ] `python -m backdown.analyze --in results/graded --out figures/` exits 0
- [ ] second run reproduces identical numbers
- [ ] caveats documented (negative discrimination, correctness sensitivity, truncation, type B absent)
- [ ] Commit + push

## Increment 9 — Report scaffold + type-B placeholder
- [ ] `report/` headings only
- [ ] neutral type-B placeholder: no numbers, no claims, no attribution, visible PLACEHOLDER marker
- [ ] `tests/test_report_placeholder.py`
- [ ] Commit + push

## Human-only / blocked
- [ ] Fill Kartik's type-A label sheet (`results/human/labels_A_evidence__kartik.csv`, 36 rows) — human only
- [ ] Type-B items, templates, raw, graded — owner delivery required; never synthesize
- [ ] Human-vs-grader report numbers — blocked on the labels above
