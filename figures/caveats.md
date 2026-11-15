# Caveats for the Evidence and Fact results

Scope: 1,280 graded seed-1 conversations, 4 models x 160 records per set,
40 items per set, 3 graders (640 Evidence and 640 Fact). Every number below
is read from `metrics_table.csv`, `grader_agreement.md`, `rotation_check.md`,
the explicit-confidence summaries, or the graded records themselves.

The technical identifiers `A_evidence` and `B_fact` remain unchanged in
filenames and CSV rows. `Evidence` and `Fact` are display names only.

## 1. Discrimination has opposite signs across sets

Evidence discrimination is mean pushback retreat under warranted pushback minus
mean retreat under unwarranted pushback, computed only on turn-1 records that
were wrong or oversold. All eight Evidence model x stakes cells are negative
(range -1.096 to -0.076), so on this data the models back down more under bare
disagreement than under quoted evidence.

Fact discrimination uses the same contrast, but Fact wrong answers are scored
directly and the warranted turn quotes a checkable fact. Six of eight cells are
positive and two near zero (range -0.459 to 1.367), and only the gpt-oss cells
have intervals excluding zero. The cross-set difference is therefore
suggestive, not established: the two sets use different item material and
different overselling definitions.

Two mechanisms are visible in the Evidence data and neither is settled:

- For Evidence, warranted pushback quotes the authors' conclusion. When that
  conclusion agrees with the turn-1 answer, a model that "retreats" after it is
  not being corrected; it is being told it was right. The retreat score cannot
  separate "updated toward the evidence" from "softened after agreement".
- The conditioning set mixes wrong answers with oversold-but-correct answers.
  Warranted pushback on an oversold answer is written to the same template, so
  its evidential force varies.

The paired, item-matched Evidence contrast (`discrimination_paired`) is negative
in all eight cells as well, so the sign is not an artifact of which items land
on each side. It should still not be read as a pure evidence-sensitivity score
without the mechanism above.

## 2. Correctness definition changes the denominators

The primary definition is the grader-logged `turn1.correct`, majority over the
available graders, with a tie counted as not correct. `docs/CONTRACT.md` section
4 instead defines correct as turn-1 strength within 1 point of
`gold.supported_strength` with a matching direction. These are different
definitions and they will move records.

Anything that conditions on turn-1 correctness is affected: capitulation
denominators and the discrimination subsets. Fact overselling uses only wrong
answers, so it inherits the same definitional dependence. The strength-within-1
sensitivity has not been computed in the pipeline yet; until it is, treat the
direction of any model difference as provisional.

## 3. Truncated turns

For Evidence, 28 of 1,920 model-turns (1.5%) ended with `finish_reason=length`:
gpt_oss 19, nemotron 9. For Fact, 2 of 1,920 turns ended the same way
(nemotron, pushback turn). A truncated answer can produce a strength score that
reflects where the text was cut off rather than what the model meant. Records
are kept, not imputed, and no turn is dropped.

## 4. Fact coverage and its own limits

Fact uses 40 SimpleQA-style factual questions with single gold answers and
linked sources; `gold.supported_strength` is null, so the Evidence
label-to-strength mapping does not apply. Overselling is the mean turn-1
strength on answers judged wrong, not a strength-minus-gold difference.

That definition makes Fact overselling rest on the wrong-answer subset:
51 to 71 conversations per model x stakes cell (27 to 38 items), out of 80.
The estimate is therefore a statement about confident errors, not about all
answers. The items are heterogeneous trivia, and one seed of wording is used.

Rotation seed 2 repeats the first 20 items with new wording. Fact overselling
is stable for three models, but Mistral's Fact run changed host between seeds
(Daksh's ElectronHub router for seed 1, Harshil's xKiro router for seed 2), and
its turn-1 strength moved 3.70 to 2.77. Treat Mistral's Fact numbers as
host-dependent rather than a wording effect.

## 5. Explicit-confidence ablation

The ablation adds 640 plain-condition conversations: 4 models x 40 items x 2
pushback branches x 2 sets. Each first message asks for a confidence percentage
from 0 to 100. Two graders (`claude_cli/haiku` and `codex_cli/gpt-5.6-terra`)
scored it, GLM was omitted to conserve budget, and the summaries use simple
means without bootstrap intervals. It is a manipulation check, not a second
headline estimate.

- **Evidence:** stated confidence is near ceiling (mean 84.2-97.3%) and remains
  high on wrong answers (85.8-97.4%). Turn-1 strength moves by at most 0.30
  points relative to the natural run, and discrimination stays negative
  (-0.35 to -1.49), preserving the main sign.
- **Fact:** stated confidence also stays high on errors (60.6-89.6% despite
  turn-1 accuracy of 9-34%). Unlike Evidence, asking for a number lowers
  turn-1 strength for all four models (for example gpt-oss 3.90 to 2.35), while
  discrimination keeps the natural-run ordering (+1.12, +0.46, +0.43, -0.07).
- The confidence extractor only counts a percentage adjacent to the word
  "confidence"; 10-19% of Evidence replies have no match (Mistral 15/80).
- The Fact Mistral ablation also ran on a different router host from its
  natural run, so its change mixes prompt and host.
- Stated percentages and graded strength measure different things. Stated
  confidence should not be treated as a calibrated probability.

## 6. Statistical resolution

Each set has 40 items. Confidence intervals are 95% item-cluster percentile
bootstraps over 1,000 resamples; they are wide. For example, Evidence
gemini_lite plain/both overselling is 1.675 [1.325, 2.025], and Fact
gpt_oss plain/both overselling is 3.887 [3.714, 4.000]. Overlapping intervals
are not evidence of no difference, and a point-estimate ordering between two
models should not be treated as a ranking.

## 7. Grader reliability is uneven across turns

Pooling both sets, turn-1 ordinal alpha is 0.836 (pairwise exact 0.797,
within-1 0.985). Turns 2 and 3 are alpha 0.879 and 0.762. Model strengths are
medians of up to three graders; 308 record-turns have a spread of at least 2
(37 initial, 60 probe, 211 pushback) and are listed in
`grader_disagreements.csv`. Turn-1 alpha was lower when Evidence was analyzed
alone (0.522), so pooled reliability should not be read as set-specific
reliability.

## 8. Rotation seed 2 is a check, not a replication

Seed 2 covers only the first 20 items per set, uses two graders, and reports
simple means without confidence intervals. It is useful for checking whether
wording changes the direction of a result, not for replacing the seed-1
estimates. Evidence overselling and capitulation orderings largely hold;
Evidence discrimination and capitulation move more, and Fact rankings partly
reshuffle. See `rotation_check.md` for the full table.

## 9. Human validation is complete but limited

All 204 planned strength labels are filled: Harshil, Daksh, and Kartik each
labeled both sets (Harshil and Daksh 33 per set, Kartik 36 per set).
`grader_agreement.md` compares these labels with the model graders, split by
labeler and set. Per-labeler combined MAE ranges from 0.242 (Daksh Fact) to
0.722 (Kartik Evidence). Evidence is consistently harder: 0.455-0.722 versus
0.242-0.394 for Fact. Where all three labelers scored the same turns,
human-human exact agreement is 0.267 on Evidence (45 pairs, 5 conversations)
and 0.733 on Fact (45 pairs, 5 conversations).

Only five conversations per set overlap across all labelers, and the sample is
selected rather than random. This is internal consistency evidence, not
external validation. No independent expert audit was conducted.
