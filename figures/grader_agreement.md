# Grader agreement

Strength scores from claude_haiku, codex, and glm. Units with fewer than
two numeric scores are excluded; missing scores are never imputed.
Exact and within-1 rates weight each available unordered grader pair equally.
Alpha uses Krippendorff's ordinal coincidence metric and pairable-unit marginals.
NA denotes no eligible data.

| Turn | Units | Pairs | Exact | Within-1 | Ordinal alpha |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 640 | 1920 | 0.685417 | 0.983854 | 0.522171 |
| 2 | 640 | 1920 | 0.654687 | 0.977604 | 0.757114 |
| 3 | 640 | 1920 | 0.593229 | 0.933333 | 0.764069 |

## Disagreements

Total record-turns with spread >= 2: 132.

- Turn 1: 21
- Turn 2: 27
- Turn 3: 84

See `grader_disagreements.csv` for grader strengths.

## Human-vs-grader comparison

No human labels yet.
