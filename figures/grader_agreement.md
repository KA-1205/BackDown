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

Filled rows: 171; blank rows: 33; invalid strengths: 0; unmatched conv_id/turn: 0.

Each human row is one comparison; missing grader scores are excluded.
Combined strength is the median of available grader scores.

### All labels

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 171 | 0.491228 | 0.578947 | 0.929825 |
| All | claude_haiku | 171 | 0.491228 | 0.578947 | 0.935673 |
| All | codex | 171 | 0.526316 | 0.561404 | 0.923977 |
| All | glm | 171 | 0.614035 | 0.543860 | 0.894737 |
| 1 | combined | 57 | 0.368421 | 0.666667 | 0.964912 |
| 1 | claude_haiku | 57 | 0.385965 | 0.649123 | 0.964912 |
| 1 | codex | 57 | 0.421053 | 0.596491 | 0.982456 |
| 1 | glm | 57 | 0.421053 | 0.631579 | 0.947368 |
| 2 | combined | 57 | 0.578947 | 0.491228 | 0.929825 |
| 2 | claude_haiku | 57 | 0.596491 | 0.473684 | 0.929825 |
| 2 | codex | 57 | 0.596491 | 0.508772 | 0.912281 |
| 2 | glm | 57 | 0.596491 | 0.491228 | 0.912281 |
| 3 | combined | 57 | 0.526316 | 0.578947 | 0.894737 |
| 3 | claude_haiku | 57 | 0.491228 | 0.614035 | 0.912281 |
| 3 | codex | 57 | 0.561404 | 0.578947 | 0.877193 |
| 3 | glm | 57 | 0.824561 | 0.508772 | 0.824561 |

### A_evidence (combined; filled 102, blank 0)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 102 | 0.607843 | 0.480392 | 0.911765 |
| 1 | combined | 34 | 0.470588 | 0.588235 | 0.941176 |
| 2 | combined | 34 | 0.647059 | 0.411765 | 0.941176 |
| 3 | combined | 34 | 0.705882 | 0.441176 | 0.852941 |

### B_fact (combined; filled 69, blank 33)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 69 | 0.318841 | 0.724638 | 0.956522 |
| 1 | combined | 23 | 0.217391 | 0.782609 | 1.000000 |
| 2 | combined | 23 | 0.478261 | 0.608696 | 0.913043 |
| 3 | combined | 23 | 0.260870 | 0.782609 | 0.956522 |

### By labeler and type (combined)

| Labeler | Type | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| daksh | A_evidence | 33 | 0.636364 | 0.484848 | 0.878788 |
| daksh | B_fact | 33 | 0.242424 | 0.787879 | 0.969697 |
| harshil | A_evidence | 33 | 0.454545 | 0.606061 | 0.939394 |
| kartik | A_evidence | 36 | 0.722222 | 0.361111 | 0.916667 |
| kartik | B_fact | 36 | 0.388889 | 0.666667 | 0.944444 |

### Inter-human agreement (strength)

Only turns scored by two or more labelers contribute.

| Type | Pairs | Conversations | MAE | Exact | Within-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A_evidence | 45 | 5 | 0.977778 | 0.266667 | 0.755556 |
| B_fact | 15 | 5 | 0.333333 | 0.666667 | 1.000000 |
