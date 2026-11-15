# Caveats for the type-A and type-B results

Scope: 1,280 graded seed-1 conversations, 4 models x 160 records per type,
40 items per type, 3 graders (640 type-A and 640 type-B). Every number below
is read from `metrics_table.csv`, `grader_agreement.md`, `rotation_check.md`,
or the graded records themselves.

## 1. Discrimination has opposite signs across types

Type-A discrimination is mean pushback retreat under warranted pushback minus
mean retreat under unwarranted pushback, computed only on turn-1 records that
were wrong or oversold. All eight type-A model x stakes cells are negative
(range -1.096 to -0.076), so on this data the models back down more under bare
disagreement than under quoted evidence.

Type-B discrimination uses the same contrast, but type-B wrong answers are
scored directly and the warranted turn quotes a checkable fact. Six of eight
cells are positive and two near zero (range -0.459 to 1.367), and only the
gpt-oss cells have intervals excluding zero. The cross-type difference is
therefore suggestive, not established: the two types use different item
material and different overselling definitions.

Two mechanisms are visible in the type-A data and neither is settled:

- For type A, warranted pushback quotes the authors' conclusion. When that
  conclusion agrees with the turn-1 answer, a model that "retreats" after it is
  not being corrected; it is being told it was right. The retreat score cannot
  separate "updated toward the evidence" from "softened after agreement".
- The conditioning set mixes wrong answers with oversold-but-correct answers.
  Warranted pushback on an oversold answer is written to the same template, so
  its evidential force varies.

The paired, item-matched type-A contrast (`discrimination_paired`) is negative
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
denominators and the discrimination subsets. Type-B overselling uses only
wrong answers, so it inherits the same definitional dependence. The
strength-within-1 sensitivity has not been computed in the pipeline yet; until
it is, treat the direction of any model difference as provisional.

## 3. Truncated turns

For type A, 28 of 1,920 model-turns (1.5%) ended with `finish_reason=length`:
gpt_oss 19, nemotron 9. For type B, 2 of 1,920 turns ended the same way
(nemotron, pushback turn). A truncated answer can produce a strength score that
reflects where the text was cut off rather than what the model meant. Records
are kept, not imputed, and no turn is dropped.

## 4. Type-B coverage and its own limits

Type B uses 40 SimpleQA-style factual questions with single gold answers and
linked sources; `gold.supported_strength` is null, so the type-A
label-to-strength mapping does not apply. Overselling is the mean turn-1
strength on answers judged wrong, not a strength-minus-gold difference.

That definition makes type-B overselling rest on the wrong-answer subset:
51 to 71 conversations per model x stakes cell (27 to 38 items), out of 80.
The estimate is therefore a statement about confident errors, not about all
answers. The items are heterogeneous trivia, and one seed of wording is used.

Rotation seed 2 repeats the first 20 items with new wording. Type-B overselling
is stable for three models, but Mistral's type-B run changed host between seeds
(Daksh's ElectronHub router for seed 1, Harshil's xKiro router for seed 2), and
its turn-1 strength moved 3.70 to 2.77. Treat Mistral's type-B numbers as
host-dependent rather than a wording effect.

## 5. Statistical resolution

Each type has 40 items. Confidence intervals are 95% item-cluster percentile
bootstraps over 1,000 resamples; they are wide. For example, type-A
gemini_lite plain/both overselling is 1.675 [1.325, 2.025], and type-B
gpt_oss plain/both overselling is 3.887 [3.714, 4.000]. Overlapping intervals
are not evidence of no difference, and a point-estimate ordering between two
models should not be treated as a ranking.

## 6. Grader reliability is uneven across turns

Pooling both types, turn-1 ordinal alpha is 0.836 (pairwise exact 0.797,
within-1 0.985). Turns 2 and 3 are alpha 0.879 and 0.762. Model strengths are
medians of up to three graders; 308 record-turns have a spread of at least 2
(37 initial, 60 probe, 211 pushback) and are listed in
`grader_disagreements.csv`. Turn-1 alpha was lower when type A was analyzed
alone (0.522), so pooled reliability should not be read as type-specific
reliability.

## 7. Rotation seed 2 is a check, not a replication

Seed 2 covers only the first 20 items per type, uses two graders, and reports
simple means without confidence intervals. It is useful for checking whether
wording changes the direction of a result, not for replacing the seed-1
estimates. Type-A overselling and capitulation orderings largely hold; type-A
discrimination and capitulation move more, and type-B rankings partly
reshuffle. See `rotation_check.md` for the full table.

## 8. Human validation is incomplete

Kartik has filled 72 strength labels: 36 type-A and 36 type-B, across 12
conversations per type. The other four label files are blank: 132 strength rows
in total (type-A and type-B Harshil and Daksh). `grader_agreement.md` compares
this one labeler's scores with the model graders, pooled and split by type.
Type-A agreement is weaker (MAE 0.722, exact 0.361) than type-B agreement
(MAE 0.389, exact 0.667). This is not an inter-human agreement estimate or a
completed multi-labeler validation.
