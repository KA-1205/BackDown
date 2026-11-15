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

Filled rows: 204; blank rows: 0; invalid strengths: 0; unmatched conv_id/turn: 0.

Each human row is one comparison; missing grader scores are excluded.
Combined strength is the median of available grader scores.

### All labels

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 204 | 0.475490 | 0.617647 | 0.926471 |
| All | claude_haiku | 204 | 0.475490 | 0.617647 | 0.931373 |
| All | codex | 204 | 0.504902 | 0.602941 | 0.921569 |
| All | glm | 204 | 0.622549 | 0.573529 | 0.887255 |
| 1 | combined | 68 | 0.323529 | 0.705882 | 0.970588 |
| 1 | claude_haiku | 68 | 0.338235 | 0.691176 | 0.970588 |
| 1 | codex | 68 | 0.352941 | 0.661765 | 0.985294 |
| 1 | glm | 68 | 0.382353 | 0.661765 | 0.955882 |
| 2 | combined | 68 | 0.500000 | 0.558824 | 0.941176 |
| 2 | claude_haiku | 68 | 0.514706 | 0.544118 | 0.941176 |
| 2 | codex | 68 | 0.529412 | 0.558824 | 0.926471 |
| 2 | glm | 68 | 0.514706 | 0.558824 | 0.926471 |
| 3 | combined | 68 | 0.602941 | 0.588235 | 0.867647 |
| 3 | claude_haiku | 68 | 0.573529 | 0.617647 | 0.882353 |
| 3 | codex | 68 | 0.632353 | 0.588235 | 0.852941 |
| 3 | glm | 68 | 0.970588 | 0.500000 | 0.779412 |

### Evidence (combined; filled 102, blank 0)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 102 | 0.607843 | 0.480392 | 0.911765 |
| 1 | combined | 34 | 0.470588 | 0.588235 | 0.941176 |
| 2 | combined | 34 | 0.647059 | 0.411765 | 0.941176 |
| 3 | combined | 34 | 0.705882 | 0.441176 | 0.852941 |

### Fact (combined; filled 102, blank 0)

| Turn | Comparison | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| All | combined | 102 | 0.343137 | 0.754902 | 0.941176 |
| 1 | combined | 34 | 0.176471 | 0.823529 | 1.000000 |
| 2 | combined | 34 | 0.352941 | 0.705882 | 0.941176 |
| 3 | combined | 34 | 0.500000 | 0.735294 | 0.882353 |

### By labeler and set (combined)

| Labeler | Set | n | MAE | Exact | Within-1 |
| --- | --- | ---: | ---: | ---: | ---: |
| daksh | Evidence | 33 | 0.636364 | 0.484848 | 0.878788 |
| daksh | Fact | 33 | 0.242424 | 0.787879 | 0.969697 |
| harshil | Evidence | 33 | 0.454545 | 0.606061 | 0.939394 |
| harshil | Fact | 33 | 0.393939 | 0.818182 | 0.909091 |
| kartik | Evidence | 36 | 0.722222 | 0.361111 | 0.916667 |
| kartik | Fact | 36 | 0.388889 | 0.666667 | 0.944444 |

### Inter-human agreement (strength)

Only turns scored by two or more labelers contribute.

| Set | Pairs | Conversations | MAE | Exact | Within-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Evidence | 45 | 5 | 0.977778 | 0.266667 | 0.755556 |
| Fact | 45 | 5 | 0.266667 | 0.733333 | 1.000000 |
