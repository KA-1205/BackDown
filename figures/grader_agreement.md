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

Filled rows: 105; blank rows: 99; invalid strengths: 0; unmatched conv_id/turn: 0.

Each human row is one comparison; missing grader scores are excluded.
Combined strength is the median of available grader scores.

### All labels

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 105 | 0.523810 | 0.542857 | 0.933333 |
| All | claude_haiku | 105 | 0.495238 | 0.561905 | 0.942857 |
| All | codex | 105 | 0.600000 | 0.504762 | 0.904762 |
| All | glm | 105 | 0.580952 | 0.552381 | 0.923810 |
| 1 | combined | 35 | 0.428571 | 0.600000 | 0.971429 |
| 1 | claude_haiku | 35 | 0.400000 | 0.628571 | 0.971429 |
| 1 | codex | 35 | 0.542857 | 0.485714 | 0.971429 |
| 1 | glm | 35 | 0.400000 | 0.628571 | 0.971429 |
| 2 | combined | 35 | 0.485714 | 0.571429 | 0.942857 |
| 2 | claude_haiku | 35 | 0.514286 | 0.542857 | 0.942857 |
| 2 | codex | 35 | 0.542857 | 0.542857 | 0.914286 |
| 2 | glm | 35 | 0.485714 | 0.571429 | 0.942857 |
| 3 | combined | 35 | 0.657143 | 0.457143 | 0.885714 |
| 3 | claude_haiku | 35 | 0.571429 | 0.514286 | 0.914286 |
| 3 | codex | 35 | 0.714286 | 0.485714 | 0.828571 |
| 3 | glm | 35 | 0.857143 | 0.457143 | 0.857143 |

### A_evidence (combined; filled 69, blank 33)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 69 | 0.594203 | 0.478261 | 0.927536 |
| 1 | combined | 23 | 0.478261 | 0.565217 | 0.956522 |
| 2 | combined | 23 | 0.478261 | 0.521739 | 1.000000 |
| 3 | combined | 23 | 0.826087 | 0.347826 | 0.826087 |

### B_fact (combined; filled 36, blank 66)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 36 | 0.388889 | 0.666667 | 0.944444 |
| 1 | combined | 12 | 0.333333 | 0.666667 | 1.000000 |
| 2 | combined | 12 | 0.500000 | 0.666667 | 0.833333 |
| 3 | combined | 12 | 0.333333 | 0.666667 | 1.000000 |

### By labeler and type (combined)

| Labeler | Type | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| harshil | A_evidence | 33 | 0.454545 | 0.606061 | 0.939394 |
| kartik | A_evidence | 36 | 0.722222 | 0.361111 | 0.916667 |
| kartik | B_fact | 36 | 0.388889 | 0.666667 | 0.944444 |

### Inter-human agreement (strength)

Only turns scored by two or more labelers contribute.

| Type | Pairs | Conversations | MAE | Exact | Within-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A_evidence | 15 | 5 | 1.000000 | 0.200000 | 0.800000 |
