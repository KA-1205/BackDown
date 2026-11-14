# Caveats for the type-A results

Scope: 640 graded type-A conversations, 4 models x 160 records, 40 items,
3 graders. Every number below is read from `metrics_table.csv`,
`grader_agreement.md`, or the graded records themselves.

## 1. Discrimination is negative in every cell

Discrimination is mean pushback retreat under warranted pushback minus mean
retreat under unwarranted pushback, computed only on turn-1 records that were
wrong or oversold. All eight model x stakes cells are negative (range
-1.096 to -0.076), so on this data the models back down more under bare
disagreement than under quoted evidence.

Two mechanisms are visible in the data and neither is settled:

- For type A, warranted pushback quotes the authors' conclusion. When that
  conclusion agrees with the turn-1 answer, a model that "retreats" after it is
  not being corrected; it is being told it was right. The retreat score cannot
  separate "updated toward the evidence" from "softened after agreement".
- The conditioning set mixes wrong answers with oversold-but-correct answers.
  Warranted pushback on an oversold answer is written to the same template, so
  its evidential force varies.

The paired, item-matched contrast (`discrimination_paired`) is negative in all
eight cells as well, so the sign is not an artifact of which items land on each
side. The sign should still not be read as a pure evidence-sensitivity score
without the mechanism above.

## 2. Correctness definition changes the denominators

The primary definition is the grader-logged `turn1.correct`, majority over the
available graders, with a tie counted as not correct. `docs/CONTRACT.md` section
4 instead defines correct as turn-1 strength within 1 point of
`gold.supported_strength` with a matching direction. These are different
definitions and they will move records.

Anything that conditions on turn-1 correctness is affected: capitulation
denominators (22, 22, 23, 22 records for the four models on plain) and the
discrimination subsets (11 to 20 records excluded per cell). The
strength-within-1 sensitivity has not been computed in the pipeline yet; until
it is, treat the direction of any model difference as provisional, and check
whether a conclusion survives both definitions before reporting it.

## 3. Truncated turns

28 of 1,920 model-turns (1.5%) ended with `finish_reason=length`: gpt_oss 19,
nemotron 9. A truncated answer can produce a strength score that reflects where
the text was cut off rather than what the model meant. The records are kept,
not imputed, and no turn is dropped; this is a small but real source of noise,
concentrated in two of the four models.

## 4. Type B is absent

There is no `data/items/B_fact.jsonl` and no type-B raw or graded results. The
CLI reports `type B_fact: no data`. No type-B metric appears in the tables and
none has been synthesized. Cross-type comparisons cannot be made from this
repository.

## 5. Statistical resolution

Each cell has 40 items. Confidence intervals are 95% item-cluster percentile
bootstraps over 1,000 resamples; they are wide, for example gemini_lite
plain/both overselling 1.675 [1.325, 2.025]. Overlapping intervals are not
evidence of no difference, and a point-estimate ordering between two models
should not be treated as a ranking.

## 6. Grader reliability is uneven across turns

Turn-1 ordinal alpha is 0.522 (pairwise exact 0.685, within-1 0.984). Turns 2
and 3 are more reliable (alpha 0.757 and 0.764). Model strengths are medians of
up to three graders; 132 record-turns have a spread of at least 2 and are listed
in `grader_disagreements.csv`. Turn-1 findings therefore carry more
grader-induced uncertainty than turns 2 and 3.

## 7. Human validation is still empty

No human strength labels have been filled in, so the human-vs-grader section
prints `No human labels yet.` Nothing in `grader_agreement.md` yet says anything
about agreement between the graders and a human expert.
