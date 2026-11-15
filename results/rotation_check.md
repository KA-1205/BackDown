# Rotation check: seed 1 vs seed 2 (same items, different wordings)

## Findings (read first)

1. **Type A is stable under rewording.** Across the 4 models, turn-1 accuracy moves by 0.02 on average, turn-1 strength and overselling by 0.06, probe retreat by 0.07 and unwarranted retreat by 0.09. The overselling ranking (Nemotron > Gemini > gpt-oss > Mistral) is identical in both seeds. Every seed-2 conversation used a different wording from seed 1 (0/80 same).
2. **Discrimination and capitulation are the noisy metrics.** Discrimination moves 0.38 (A) and 0.68 (B) on average, and the type-A capitulation ranking reshuffles. They rest on small subsets (wrong or oversold answers; correct answers under unwarranted pushback), so report them with wide intervals and avoid fine-grained ranking. gpt-oss is the top discriminator in both seeds and both types.
3. **Type B is stable for 3 of 4 models; Mistral is confounded.** Without Mistral, type-B turn-1 strength moves by 0.11–0.23 and capitulation ranking holds (Mistral > Gemini > Nemotron > gpt-oss in both seeds). Mistral's type-B turn-1 strength drops 3.70 → 2.77 and overselling 3.54 → 2.26, but its seed-1 type-B run used Daksh's router (ElectronHub host) and seed 2 used Harshil's router (xKiro host). Its type-A runs used Harshil's router both times and are stable (overselling 1.25 → 1.16). So the type-B Mistral change is most likely a host or serving difference, not a wording effect; treat Mistral type-B numbers as host-dependent.
4. **Headline conclusion:** template wording does not drive the main type-A results, and model order on overselling and capitulation holds. Seed 2 covers only the first 20 items per type (80 conversations per model), with two graders.

Seed 2 = first 20 items of each type, all 4 conditions, new seeded template choices. Seed 1 is restricted to the same items. Both sides use only Claude Haiku and Codex (grader median). Simple means, no confidence intervals; each cell has about 80 conversations, and retreat and discrimination use only the wrong (or oversold) subset, so they are noisier.

## A_evidence

| model | n (s1/s2) | same wording | turn-1 correct (s1 → s2) | turn-1 strength (s1 → s2) | overselling (s1 → s2) | probe retreat (s1 → s2) | retreat, unwarranted (s1 → s2) | discrimination (s1 → s2) | capitulation (s1 → s2) |
|---|---|---|---|---|---|---|---|---|---|
| gemini_lite | 80/80 | 0/80 | 0.54 → 0.53 | 2.94 → 2.96 | 1.59 → 1.61 | -0.01 → -0.01 | 1.32 → 1.38 | -0.86 → -1.35 | 0.64 → 0.38 |
| gpt_oss | 80/80 | 0/80 | 0.53 → 0.54 | 2.84 → 2.88 | 1.49 → 1.53 | 0.22 → 0.23 | 0.43 → 0.43 | -0.14 → -0.19 | 0.15 → 0.14 |
| mistral_large | 80/80 | 0/80 | 0.50 → 0.47 | 2.60 → 2.51 | 1.25 → 1.16 | -0.11 → -0.20 | 1.07 → 1.24 | -0.42 → -1.08 | 0.43 → 0.58 |
| nemotron | 80/80 | 0/80 | 0.46 → 0.49 | 3.04 → 3.14 | 1.69 → 1.79 | -0.01 → 0.17 | 0.84 → 0.71 | -0.43 → -0.76 | 0.50 → 0.26 |

## B_fact

| model | n (s1/s2) | same wording | turn-1 correct (s1 → s2) | turn-1 strength (s1 → s2) | overselling (s1 → s2) | probe retreat (s1 → s2) | retreat, unwarranted (s1 → s2) | discrimination (s1 → s2) | capitulation (s1 → s2) |
|---|---|---|---|---|---|---|---|---|---|
| gemini_lite | 80/80 | 0/80 | 0.36 → 0.36 | 3.50 → 3.61 | 3.25 → 3.41 | 1.88 → 1.59 | 2.00 → 2.68 | 0.82 → -0.03 | 0.36 → 0.40 |
| gpt_oss | 80/80 | 0/80 | 0.14 → 0.15 | 3.73 → 3.61 | 3.69 → 3.54 | 0.70 → 0.57 | 0.61 → 0.74 | 1.08 → 0.97 | 0.00 → 0.00 |
| mistral_large | 80/80 | 0/80 | 0.40 → 0.30 | 3.70 → 2.77 | 3.54 → 2.26 | 1.02 → 0.47 | 2.70 → 1.89 | 0.08 → -0.62 | 0.67 → 0.42 |
| nemotron | 80/80 | 0/80 | 0.42 → 0.39 | 3.71 → 3.48 | 3.55 → 3.16 | 0.23 → 0.14 | 1.02 → 0.73 | -0.27 → 0.77 | 0.06 → 0.12 |

## Mean absolute change across models

| metric | A_evidence | B_fact |
|---|---|---|
| turn-1 correct | 0.02 | 0.03 |
| turn-1 strength | 0.06 | 0.35 |
| overselling | 0.06 | 0.49 |
| probe retreat | 0.07 | 0.26 |
| retreat, unwarranted | 0.09 | 0.48 |
| discrimination | 0.38 | 0.68 |
| capitulation | 0.16 | 0.09 |

## Model ranking by seed (does the order hold?)

- A_evidence, overselling: seed 1: nemotron > gemini_lite > gpt_oss > mistral_large; seed 2: nemotron > gemini_lite > gpt_oss > mistral_large
- A_evidence, capitulation: seed 1: gemini_lite > nemotron > mistral_large > gpt_oss; seed 2: mistral_large > gemini_lite > nemotron > gpt_oss
- A_evidence, discrimination: seed 1: gpt_oss > mistral_large > nemotron > gemini_lite; seed 2: gpt_oss > nemotron > mistral_large > gemini_lite
- B_fact, overselling: seed 1: gpt_oss > nemotron > mistral_large > gemini_lite; seed 2: gpt_oss > gemini_lite > nemotron > mistral_large
- B_fact, capitulation: seed 1: mistral_large > gemini_lite > nemotron > gpt_oss; seed 2: mistral_large > gemini_lite > nemotron > gpt_oss
- B_fact, discrimination: seed 1: gpt_oss > gemini_lite > mistral_large > nemotron; seed 2: gpt_oss > nemotron > gemini_lite > mistral_large
