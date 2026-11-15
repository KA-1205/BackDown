# Grader agreement

Strength scores from claude_haiku, codex, and glm. Units with fewer than
two numeric scores are excluded; missing scores are never imputed.
Exact and within-1 rates weight each available unordered grader pair equally.
Alpha uses Krippendorff's ordinal coincidence metric and pairable-unit marginals.
NA denotes no eligible data.

| Turn | Units | Pairs | Exact | Within-1 | Ordinal alpha |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1280 | 3840 | 0.797396 | 0.985156 | 0.836139 |
| 2 | 1280 | 3840 | 0.750781 | 0.974219 | 0.878663 |
| 3 | 1280 | 3840 | 0.681771 | 0.902865 | 0.762354 |

## Disagreements

Total record-turns with spread >= 2: 308.

- Turn 1: 37
- Turn 2: 60
- Turn 3: 211

See `grader_disagreements.csv` for grader strengths.

## Human-vs-grader comparison

Filled rows: 36; blank rows: 168; invalid strengths: 0; unmatched conv_id/turn: 0.

Each human row is one comparison; missing grader scores are excluded.
Combined strength is the median of available grader scores.

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 36 | 0.722222 | 0.361111 | 0.916667 |
| All | claude_haiku | 36 | 0.666667 | 0.388889 | 0.944444 |
| All | codex | 36 | 0.777778 | 0.361111 | 0.861111 |
| All | glm | 36 | 0.611111 | 0.444444 | 0.944444 |
| 1 | combined | 12 | 0.583333 | 0.500000 | 0.916667 |
| 1 | claude_haiku | 12 | 0.583333 | 0.500000 | 0.916667 |
| 1 | codex | 12 | 0.666667 | 0.416667 | 0.916667 |
| 1 | glm | 12 | 0.583333 | 0.500000 | 0.916667 |
| 2 | combined | 12 | 0.750000 | 0.250000 | 1.000000 |
| 2 | claude_haiku | 12 | 0.750000 | 0.250000 | 1.000000 |
| 2 | codex | 12 | 0.833333 | 0.250000 | 0.916667 |
| 2 | glm | 12 | 0.583333 | 0.416667 | 1.000000 |
| 3 | combined | 12 | 0.833333 | 0.333333 | 0.833333 |
| 3 | claude_haiku | 12 | 0.666667 | 0.416667 | 0.916667 |
| 3 | codex | 12 | 0.833333 | 0.416667 | 0.750000 |
| 3 | glm | 12 | 0.666667 | 0.416667 | 0.916667 |
