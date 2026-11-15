# BackDown: Comparing Initial and Defended Claim Strength Under Challenge

**Authors:** Kartik Arora (kartikarora.1205@outlook.com), Harshil Srivastav (thisisharshil@gmail.com), Daksh Goel (iamdaksh23@gmail.com)

**Affiliations:** Kartik Arora, Harshil Srivastav, and Daksh Goel — Department of Artificial Intelligence and Machine Learning, School of Engineering & Technology, Vivekananda Institute of Professional Studies – Technical Campus, AU-Block, Outer Ring Road, Pitampura, Delhi 110034, India.
Research conducted at the AI x Epistemics Research Sprint, November 2026, with Apart Research.

## Abstract

An assistant can sound convincing initially yet weaken its answer when challenged. Separating responsiveness to evidence from responsiveness to disagreement requires measuring claim strength before and after both kinds of pressure. BackDown compares initial, neutrally probed, and defended claim strength across two 40-item sets: Evidence, comprising PubMedQA study summaries with weak or ambiguous evidence, and Fact, comprising short questions with single answers. We analyze 1,280 conversations from four API-served models under two pushback and two stakes conditions, using median scores from three model graders, plus a 640-conversation explicit-confidence ablation. Evidence mean initial overselling ranges from 1.45 to 1.84 strength points without stakes and 1.28 to 1.56 with stakes; warranted-minus-unwarranted retreat is negative in every cell. Fact overselling, defined as turn-1 strength on wrong answers, ranges from 3.44 to 3.89, and its discrimination contrast is positive in six of eight cells, with intervals excluding zero only for gpt-oss. Asking for a confidence percentage leaves Evidence strength nearly unchanged but lowers Fact strength in all four models while stated confidence remains high on errors. A seed-2 wording rotation largely preserves Evidence overselling. Pooled ordinal grader agreement ranges from 0.762 to 0.879. Against 204 human labels from three authors, median graders show mean absolute error 0.242–0.722 across labeler–set groups; human–human exact agreement is 0.267 on Evidence and 0.733 on Fact. The results are descriptive and do not establish a model ranking.

## 1. Introduction

Users may act on an assistant's first answer without discovering how readily it changes under questioning. Answer accuracy alone does not describe this conversational stability. Equally, changing an answer is not inherently undesirable: a useful assistant should reconsider genuine evidence without simply adopting unsupported disagreement.

BackDown measures initial claim strength and strength retained after probing and challenge. It tests two item sets. **Evidence** (`A_evidence`) uses biomedical study summaries whose evidence is weak or ambiguous, so a confident answer may exceed what the abstract supports. **Fact** (`B_fact`) uses short factual questions with a single correct answer, so errors are unambiguous and confident mistakes are directly visible. The contributions are a reproducible evidence-versus-disagreement protocol, two item sets with contrasting demands, a stakes manipulation, a wording-rotation check, an explicit-confidence manipulation check, and reliability-aware analysis. The goal is to distinguish useful updating from social compliance while testing the validity of that distinction.

The sprint's **MisleadBench** and **FlipRate** example projects were the starting point: MisleadBench proposes scoring the gap between what a model implies and what it will defend across turns, and FlipRate proposes measuring answer and confidence changes across escalating rebuttals (Apart Research, 2026; https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15). BackDown adds strength trajectories, an explicit evidence control, stakes conditions, a second item set, and grader- and human-reliability analysis.

## 2. Related Work

PubMedQA supplies biomedical questions, abstracts without conclusions, conclusion text, and yes/no/maybe labels (Jin et al., 2019). We reuse these components to study conversational revision rather than only question-answering accuracy. SimpleQA supplies short, adversarially collected factual questions with a single indisputable answer, which makes confident errors easy to identify (Wei et al., 2024).

SycEval studies sycophancy under rebuttals, distinguishing changes toward correct and incorrect answers (Fanous et al., 2025). ELEPHANT measures social sycophancy as excessive preservation of a user's face, including cases where no explicit factual claim is at stake (Cheng et al., 2025). BackDown complements this work with a neutral intermediate probe, ordinal strength trajectories, and an explicit warranted-versus-unwarranted contrast. MASK distinguishes honesty from accuracy and evaluates lying under pressure (Ren et al., 2025). BackDown instead measures observable language and stance changes, without establishing internal beliefs or deceptive intent. These comparisons motivate the protocol, not superiority over prior benchmarks.

## 3. Methods

### 3.1 Data and conversations

The analyzed snapshot contains **1,280 successful, unique conversations**: 640 Evidence records and 640 Fact records, each set covering 40 items × four models × two stakes conditions × two pushback conditions. Each model contributes 160 records per set. All analyzed records use `variant=natural` and seed 1; no errored or duplicate record occurs in this snapshot.

Evidence uses 40 PubMedQA-derived items: 20 `maybe`, 10 `no`, and 10 `yes`. Fact uses 40 SimpleQA-style questions spanning heterogeneous topics; each has one gold answer, linked sources, and no `supported_strength`, so the Evidence label-to-strength mapping does not apply. Fact items were selected for short, checkable answers rather than for biomedical content.

The first message presents the item. A neutral follow-up asks, for example, “To be clear, how sure are you about that conclusion?” The final message quotes supporting material or supplies unsupported disagreement, such as “I don't think that's right.” Stakes prompts add a hypothetical imminent decision. Wording is in `templates/A_evidence.json` and `templates/B_fact.json`; realized prompts are logged in `messages`.

Conditions use separate conversations rather than branching from an identical initial response. `backdown/run.py` selects templates deterministically using item, seed, stakes, and pushback condition. Thus condition changes can also change prompt wording. This matters especially for interpreting stakes contrasts. A seed-2 rotation repeats the first 20 items of each set with new wording; it is a robustness check, not a second full sample.

A separate **explicit-confidence ablation** adds 640 conversations: four models × 40 items × two pushback branches × two sets, plain condition only. The first message also asks for a confidence percentage from 0 to 100. The ablation has no stakes conditions, two graders, and no bootstrap intervals; §4.6 reports it separately from the main estimates.

### 3.2 Models and grading

Logged subject routes are Gemini `gemini-3.5-flash-lite`; Mistral requested as `mistral-large-3` through FreeLLMAPI, returning `mistralai/mistral-large-2512`; `openai/gpt-oss-120b` through OpenRouter and Groq; and NVIDIA `nvidia/nemotron-3-ultra-550b-a55b`. Model names here denote logged API identities. Configured subject settings are temperature 0.7, a 3,000-token output limit, and the system prompt “You are a helpful assistant.” Configuration is not proof of provider-side determinism.

The main 1,280-conversation sample has grades from three graders: `claude_cli/haiku`, `codex_cli/gpt-5.6-terra`, and `openrouter/z-ai/glm-5.3-flash`. The 640-conversation explicit-confidence ablation has two graders, `claude_cli/haiku` and `codex_cli/gpt-5.6-terra`; GLM was omitted to conserve the OpenRouter budget. Graders see the transcript and the gold answer or conclusion. Strength is scored from 0 (rejects or abandons the claim), through 1 (heavily hedged), 2 (moderate), and 3 (strong), to 4 (certain/unqualified). Later turns refer to the initial claim. Analysis takes the available-score median; boolean correctness and answer-change judgments use majority votes, with ties treated as unknown rather than imputed.

The implemented grading prompt defines initial correctness by stance or answer matching the gold label. This differs from `docs/CONTRACT.md`, which additionally requires Evidence strength within one point of supported strength. **The logged-correctness versus CONTRACT sensitivity analysis has not been computed.** Correctness-conditioned comparisons are consequently provisional.

### 3.3 Metrics and uncertainty

Let Sₜ be median strength at turn t. For Evidence, let G be the supported strength mapped from the item label: yes → 3, maybe → 1, no → 0.

- **Evidence overselling:** mean S₁ − G, retaining signed differences.
- **Fact overselling:** mean S₁ among answers majority-judged wrong. This measures confidence on errors, not strength minus gold.
- **Probe retreat:** mean S₁ − S₂.
- **Discrimination:** mean S₁ − S₃ under warranted pushback minus its mean under unwarranted pushback, restricted separately to records judged incorrect or with S₁ > G. For Fact, the eligible set is wrong answers.
- **Paired discrimination:** the same contrast on items eligible in both pushback conditions.
- **Capitulation:** the fraction with majority-judged answer change among majority-correct initial answers receiving unwarranted pushback.
- **Stakes contrast:** mean matched-item stakes-minus-plain difference, averaging eligible repeated records within each condition.

Intervals are 95% item-cluster percentile bootstraps with 1,000 resamples, preserving dependence among records from the same item. `backdown/analyze.py` uses deterministic row-specific seed offsets from 12345. Intervals characterize item-sampling uncertainty conditional on the recorded generations and grades, not all uncertainty in the measurement procedure. The explicit-confidence ablation uses simple means without intervals.

## 4. Results

### 4.1 Evidence: weak and ambiguous study summaries

Figure 1 and Table 1 summarize the Evidence headline metrics. Every cell has positive mean overselling under the specified mapping and negative discrimination.

![Overselling and discrimination for each subject model under plain and stakes framing.](../figures/headline.png)

**Figure 1. Evidence initial overselling and warranted-minus-unwarranted retreat.** Open markers show plain prompts; filled markers show stakes prompts; arrows connect conditions within a model. Error bars are 95% item-cluster bootstrap intervals. Overselling pools both pushback branches; discrimination uses incorrect-or-oversold initial records. Source: `figures/headline.png`, using `figures/metrics_table.csv` rows with `type=A_evidence`, `metric=overselling, pushback=both` and `metric=discrimination, pushback=warranted_minus_unwarranted`. These axes are operational scores, not validated model-quality rankings.

**Table 1. Evidence headline estimates, in strength-scale points.** Brackets give 95% bootstrap intervals. Overselling uses 80 conversations over 40 items per row. The final column gives discrimination's eligible conversations/unique items. Source: the CSV row filters specified in Figure 1, selected by model and stakes condition.

| Model key | Condition | Overselling [95% CI] | Discrimination [95% CI] | Eligible n/items |
|---|---|---:|---:|---:|
| `gemini_lite` | Plain | 1.675 [1.325, 2.025] | −1.096 [−1.683, −0.423] | 62/32 |
| `gemini_lite` | Stakes | 1.500 [1.075, 1.900] | −0.750 [−1.289, −0.242] | 64/33 |
| `gpt_oss` | Plain | 1.675 [1.288, 2.050] | −0.630 [−0.882, −0.363] | 64/34 |
| `gpt_oss` | Stakes | 1.312 [0.900, 1.725] | −0.076 [−0.362, 0.225] | 66/35 |
| `mistral_large` | Plain | 1.450 [1.050, 1.850] | −0.800 [−1.367, −0.299] | 60/30 |
| `mistral_large` | Stakes | 1.275 [0.875, 1.663] | −0.681 [−1.180, −0.190] | 62/33 |
| `nemotron` | Plain | 1.837 [1.450, 2.175] | −0.680 [−1.319, −0.037] | 66/35 |
| `nemotron` | Stakes | 1.562 [1.163, 1.900] | −0.859 [−1.302, −0.478] | 69/36 |

Negative discrimination means that eligible records show greater average retreat after bare disagreement than after quoted evidence. All eight paired-discrimination point estimates are also negative (`metric=discrimination_paired`), so restricting to matched eligible items preserves the sign. It does not resolve the construct problem: a quoted conclusion can agree with the initial answer, and oversold-but-correct answers enter the same subset as incorrect answers.

Paired overselling differences associated with stakes are −0.175 for Gemini, −0.363 for gpt-oss, −0.175 for Mistral, and −0.275 for Nemotron (`stakes=stakes_minus_plain, pushback=both, metric=overselling`); every interval excludes zero. These are descriptive condition contrasts, not isolated causal effects of stakes.

Plain-condition capitulation is 15/22 (68.2%) for Gemini, 3/22 (13.6%) for gpt-oss, 15/23 (65.2%) for Mistral, and 8/22 (36.4%) for Nemotron. Source: `stakes=plain, pushback=unwarranted, metric=capitulation`; numerators are `value × n`. These small, grader-selected denominators and the unresolved correctness definition preclude treating their ordering as a reliable ranking.

### 4.2 Fact: short factual questions

Fact is much harder: plain-condition turn-1 accuracy is 27/80 (33.8%) for Gemini, 9/80 (11.3%) for gpt-oss, 26/80 (32.5%) for Mistral, and 29/80 (36.3%) for Nemotron. Figure 2 and Table 2 summarize the Fact metrics. Overselling here is the mean turn-1 strength on wrong answers, so values near 4 mean that errors are stated with near-certainty.

![Overselling and discrimination for each subject model on Fact questions.](../figures/headline_B_fact.png)

**Figure 2. Fact overselling on wrong answers and warranted-minus-unwarranted retreat.** Open markers show plain prompts; filled markers show stakes prompts; arrows connect conditions within a model. Error bars are 95% item-cluster bootstrap intervals. Overselling uses answers majority-judged wrong; discrimination uses the same wrong-answer subset. Source: `figures/headline_B_fact.png`, using the `type=B_fact` rows in `figures/metrics_table.csv` selected by the same metric and pushback filters as Figure 1.

**Table 2. Fact headline estimates, in strength-scale points.** Brackets give 95% bootstrap intervals. Overselling is mean turn-1 strength on wrong answers; the scale runs from 0 to 4. Discrimination is warranted-minus-unwarranted retreat on the same wrong-answer subset. The final column gives eligible conversations/unique items. Source: `figures/metrics_table.csv`, rows with `type=B_fact`.

| Model key | Condition | Overselling [95% CI] | Discrimination [95% CI] | Eligible n/items |
|---|---|---:|---:|---:|
| `gemini_lite` | Plain | 3.585 [3.208, 3.906] | 0.459 [−0.302, 1.185] | 53/28 |
| `gemini_lite` | Stakes | 3.455 [3.070, 3.778] | 0.525 [−0.601, 1.506] | 55/29 |
| `gpt_oss` | Plain | 3.887 [3.714, 4.000] | 1.367 [0.600, 2.046] | 71/38 |
| `gpt_oss` | Stakes | 3.676 [3.406, 3.886] | 0.770 [0.094, 1.483] | 71/38 |
| `mistral_large` | Plain | 3.778 [3.589, 3.942] | 0.582 [−0.060, 1.234] | 54/31 |
| `mistral_large` | Stakes | 3.442 [3.098, 3.750] | −0.221 [−1.045, 0.590] | 52/28 |
| `nemotron` | Plain | 3.725 [3.440, 3.960] | 0.592 [−0.566, 1.766] | 51/27 |
| `nemotron` | Stakes | 3.473 [3.019, 3.855] | −0.459 [−1.364, 0.369] | 55/32 |

Six of eight Fact discrimination cells are positive, the opposite sign from Evidence, but only the two gpt-oss intervals exclude zero. The paired, item-matched contrast is likewise positive and excludes zero only for gpt-oss: 1.303 [0.576, 2.061] plain and 0.727 [0.030, 1.394] stakes. Every other Fact paired interval includes zero. The sign difference between sets is therefore suggestive rather than established, because the two sets use different material and different overselling definitions.

Plain-condition Fact capitulation is 4/13 (30.8%) for Gemini, 1/4 (25.0%) for gpt-oss, 9/12 (75.0%) for Mistral, and 0/15 (0%) for Nemotron. These denominators are very small, so the ordering is not informative on its own. Stakes are associated with lower Fact overselling in all four models, but only the gpt-oss and Mistral intervals exclude zero (−0.197 [−0.447, −0.026] and −0.333 [−0.685, −0.019]).

### 4.3 Rotation check (seed 2)

Seed 2 repeats the first 20 items of each set with different wording, two graders, and simple means (no bootstrap intervals). For Evidence, mean absolute change is 0.02 for turn-1 accuracy, 0.06 for turn-1 strength, 0.06 for overselling, 0.07 for probe retreat, and 0.09 for unwarranted retreat. The Evidence overselling ranking is identical across seeds (Nemotron > Gemini > gpt-oss > Mistral). Evidence discrimination and capitulation move more (mean absolute changes 0.38 and 0.16), so those metrics are the least stable under rewording.

For Fact, mean absolute change is 0.35 for turn-1 strength, 0.49 for overselling, and 0.68 for discrimination. Excluding Mistral, Fact turn-1 strength moves 0.11 to 0.23. Mistral's Fact seed-1 run used a different router host from seed 2, and its turn-1 strength moved from 3.70 to 2.77; its Fact numbers are therefore host-dependent rather than a clean wording comparison. The rotation check supports the direction of the main Evidence result, but it is not a replication: it covers half the items, uses two graders, and omits confidence intervals.

### 4.4 Grader reliability

Table 3 shows agreement among model graders, not agreement with human experts. It pools both sets and all seed-1 records.

**Table 3. Strength-score agreement by conversational turn, pooled across both sets.** Each row contains 1,280 conversation-turn units and 3,840 available unordered grader pairs. Exact and within-one rates pool those pairs; alpha uses ordinal coincidence distances. Source: `figures/grader_agreement.md`, reproduced from the graded records.

| Turn | Exact agreement | Within one point | Ordinal alpha |
|---|---:|---:|---:|
| Initial | 0.797 | 0.985 | 0.836 |
| Neutral probe | 0.751 | 0.974 | 0.879 |
| Pushback | 0.682 | 0.903 | 0.762 |

There are 308 conversation-turns with grader spread of at least two points: 37 initial, 60 probe, and 211 pushback turns (`figures/grader_disagreements.csv`). Pooled reliability is higher than Evidence-only reliability was: turn-1 ordinal alpha for Evidence alone is 0.522. The pooled figures therefore should not be read as set-specific reliability, and the pushback turn remains the noisiest.

### 4.5 Human versus grader

All three authors completed strength labels: **204 rows, none blank**. Harshil and Daksh each labeled 33 Evidence and 33 Fact rows (11 conversations per set); Kartik labeled 36 of each (12 conversations per set). The 204 rows are repeated turns within 48 unique conversations; 68 labeler–conversation assignments cover 24 conversations per set. Five conversations per set were scored by all three labelers, and the rest by one. The comparison reports zero invalid strengths and zero unmatched conversation/turn identifiers.

Pooled across all labels, median grader strength has MAE 0.475, exact agreement 0.618, and within-one agreement 0.926. Agreement is best on the initial turn (MAE 0.324, exact 0.706), weaker on the neutral probe (0.500, 0.559), and weakest after pushback (0.603, 0.588). By set, the Evidence labels agree less closely (MAE 0.608, exact 0.480) than the Fact labels (MAE 0.343, exact 0.755).

**Table 4. Human strength labels versus combined grader strength, by labeler and set.** MAE is mean absolute error in strength-scale points; exact and within-one agreement are proportions. Combined strength is the median of available grader scores. Inter-human comparisons are reported in the text and in `figures/grader_agreement.md`. Source: the `### By labeler and set (combined)` rows in `figures/grader_agreement.md`, using all six filled label files, `results/human/labels_{A_evidence,B_fact}__{harshil,kartik,daksh}.csv`.

| Labeler | Set | n | MAE | Exact agreement | Within one point |
|---|---|---:|---:|---:|---:|
| Harshil | Evidence | 33 | 0.454545 | 0.606061 | 0.939394 |
| Daksh | Evidence | 33 | 0.636364 | 0.484848 | 0.878788 |
| Kartik | Evidence | 36 | 0.722222 | 0.361111 | 0.916667 |
| Harshil | Fact | 33 | 0.393939 | 0.818182 | 0.909091 |
| Daksh | Fact | 33 | 0.242424 | 0.787879 | 0.969697 |
| Kartik | Fact | 36 | 0.388889 | 0.666667 | 0.944444 |

Where all three labelers scored the same five conversations per set, human–human agreement is MAE 0.978 and exact 0.267 on Evidence (45 pairs) and MAE 0.267 and exact 0.733 on Fact (45 pairs). The graders therefore agree with individual labelers about as closely as the labelers agree with one another; on Evidence, human disagreement is larger than grader–human disagreement. This is internal consistency evidence from a small, selected sample, not external validation. No independent expert audit was conducted.

### 4.6 Explicit-confidence ablation

The explicit-confidence ablation asks the model to state a percentage confidence on the first turn and uses the plain condition only. It has 80 conversations per model per set, two graders, and no confidence intervals. Table 5 and Table 6 report the two experiments separately.

#### 4.6.1 Evidence

Table 5 summarizes the Evidence ablation. Stated confidence is uniformly high: mean 84.2% to 97.3%, and means on wrong answers are within about two points of the overall means (85.8% to 97.4%, 33 to 42 wrong answers per model). Turn-1 strength changes by at most 0.30 points relative to the natural plain-condition run. Overselling remains positive (1.30 to 1.94) and discrimination remains negative for all four models (−0.35 to −1.49), preserving the main Evidence sign. Retreat under bare disagreement is mixed: it rises for Gemini (1.73 → 2.06), falls for gpt-oss (0.75 → 0.45) and Mistral (1.30 → 0.84), and is essentially unchanged for Nemotron (1.00 → 0.97).

**Table 5. Evidence explicit-confidence ablation, plain condition only.** Stated confidence is the last “confidence … NN%” in the turn-1 reply; wrong-answer cells give the mean and the number of wrong answers. Strength and discrimination use the grader median under the same definitions as Table 1. Source: `results/sanity_A_evidence__explicit_confidence.md`, 80 conversations per model, two graders, simple means, no confidence intervals.

| Model | Turn-1 correct | Mean stated confidence | Stated confidence when wrong (n) | Turn-1 strength, ablation → natural | Discrimination |
|---|---:|---:|---:|---:|---:|
| Gemini | 48% | 97.3% | 97.4% (42) | 3.19 → 2.92 | −1.49 |
| gpt-oss | 51% | 87.0% | 85.8% (33) | 2.80 → 2.92 | −0.35 |
| Mistral | 54% | 84.2% | 87.0% (33) | 2.55 → 2.70 | −1.16 |
| Nemotron | 51% | 91.0% | 91.7% (36) | 2.98 → 3.09 | −0.93 |

#### 4.6.2 Fact

Table 6 summarizes the Fact ablation. Stated confidence again stays high on errors: overall means are 62.8% to 92.9%, and wrong-answer means are 60.6% to 89.6% (49 to 72 wrong answers per model), despite turn-1 accuracy of 9% to 34%. Unlike Evidence, asking for a number lowers turn-1 strength for all four models: gpt-oss 3.90 → 2.35, Mistral 3.84 → 2.98, Nemotron 3.81 → 3.26, and Gemini 3.71 → 3.45. Overselling remains high (2.27 to 3.21). Discrimination stays positive for three models (+0.43 to +1.12) and is slightly negative for Nemotron (−0.07), the same ordering as the natural Fact run. Retreat under bare disagreement falls for Gemini (2.48 → 2.19), gpt-oss (0.90 → 0.38), and Mistral (3.08 → 2.01), and rises for Nemotron (0.45 → 1.04).

**Table 6. Fact explicit-confidence ablation, plain condition only.** Stated confidence is the last “confidence … NN%” in the turn-1 reply; wrong-answer cells give the mean and the number of wrong answers. Strength and discrimination use the grader median under the same definitions as Table 2. Source: `results/sanity_B_fact__explicit_confidence.md`, 80 conversations per model, two graders, simple means, no confidence intervals.

| Model | Turn-1 correct | Mean stated confidence | Stated confidence when wrong (n) | Turn-1 strength, ablation → natural | Discrimination |
|---|---:|---:|---:|---:|---:|
| Gemini | 34% | 92.9% | 89.6% (49) | 3.45 → 3.71 | +0.43 |
| gpt-oss | 9% | 62.8% | 60.6% (72) | 2.35 → 3.90 | +1.12 |
| Mistral | 19% | 78.6% | 74.4% (65) | 2.98 → 3.84 | +0.46 |
| Nemotron | 32% | 88.0% | 84.6% (54) | 3.26 → 3.81 | −0.07 |

The ablation has two important limits. The confidence extractor only counts a percentage adjacent to the word “confidence”, and 10% to 19% of Evidence replies have no match (Mistral 15/80). The Fact Mistral ablation also ran on a different router host from its natural run, so its change mixes prompt and host. These results are manipulation checks on a plain-only, two-grader subsample, not second headline estimates.

## 5. Discussion and Limitations

The two item sets produce different descriptive patterns. Evidence shows more retreat after bare disagreement than after quoted evidence, while Fact shows the opposite sign in most cells. We do not interpret this as Fact models being more epistemically virtuous. The sets differ in material, difficulty, and metric construction: Evidence discrimination mixes wrong and oversold-but-correct answers and its warranted turn can merely confirm the initial claim, whereas Fact discrimination is computed only on unambiguously wrong answers and its warranted turn supplies a checkable fact. Only the gpt-oss Fact intervals exclude zero, so the cross-set contrast is a hypothesis for follow-up, not a finding.

Fact overselling is also a different construct from Evidence overselling. It measures how strongly models state wrong answers, not how far an answer exceeds the evidence. Values near 4 on a 0–4 scale mean that errors are delivered with near-certainty, which is concerning for decision support, but the estimate rests on the wrong-answer subset (51 to 71 conversations per cell). The 40 Fact items are heterogeneous trivia, and one wording seed cannot establish robustness across factual domains.

There is a directional ambiguity in Evidence overselling: graders score the model's own main claim, whereas the supported-strength mapping is anchored to the question's affirmative proposition. A strongly stated negative answer can therefore receive a high score despite a `no` label mapped to zero. Resolving claim orientation is necessary before interpreting Evidence overselling as literal evidential exaggeration.

The explicit-confidence ablation shows that requesting a number changes tone differently by set. On Evidence, stated confidence is near ceiling and graded strength barely moves. On Fact, all four models reduce graded strength while their spoken confidence stays high on errors. Stated percentages and graded strength therefore measure different things, and stated confidence should not be treated as a calibrated probability. The ablation is plain-only, two-grader, and interval-free, so it is a manipulation check rather than a second main result.

The study is small, English-only, and built from two narrow item sets. One full seed does not demonstrate rotation robustness; the seed-2 check covers half the items, two graders, and no intervals. Stakes and other template wording can change together; separate conversations introduce generation variability. Grader consensus is not ground truth, and the bootstrap does not incorporate systematic grader bias. The logged-correctness versus CONTRACT sensitivity remains uncomputed.

All three authors' strength labels are complete, providing a human–grader comparison across both sets and all six labeler–set groups. Evidence agreement differs noticeably by labeler (MAE 0.455–0.722) and is weaker than Fact agreement (0.242–0.394), mirroring the difficulty difference in the item sets. Human–human agreement is also weaker on Evidence (exact 0.267) than on Fact (0.733), and is no closer than grader–human agreement. Because only five conversations per set are shared by all labelers and the sample is selected rather than random, this is internal consistency evidence, not external validation.

## 6. Conclusion

The conversations show positive mapped overselling on both sets: Evidence answers exceed weak evidence, and Fact wrong answers are stated with near-certainty. Evidence retreat is larger under bare disagreement than under quoted evidence, while Fact evidence suggests the opposite direction, significantly so only for gpt-oss. Asking for a confidence percentage leaves Evidence strength nearly unchanged but makes Fact answers more hedged, without removing their errors. These reproducible descriptive findings depend on claim orientation, item difficulty, evidential relevance, and correctness definitions. Independent expert validation and the correctness sensitivity take priority over declaring a model ranking.

## 7. Future Work

- **Consumer chat-app side study.** The planned protocol for about 20 hand-run conversations in the ChatGPT and Claude consumer apps was not executed, and no `results/chat_app/` data exist. We list it as future work only; no chat-app result is reported.
- **CONTRACT-correctness sensitivity.** Recompute correctness-conditioned metrics with the `docs/CONTRACT.md` rule that also requires Evidence strength within one point of supported strength.
- **Independent expert grading.** The three-author labels are internal consistency evidence, not an external audit.
- **Direction-aligned scoring.** Align the graded claim with the item's affirmative proposition before interpreting Evidence overselling.
- **Evidence-relation stratification.** Separate quoted evidence that supports, contradicts, or is irrelevant to the initial claim.
- **Matched wording across seeds.** Extend the rotation check to all items with the same grader set and bootstrap intervals.

## Code and Data

- **Repository:** [github.com/KA-1205/BackDown](https://github.com/KA-1205/BackDown).
- **Datasets:** [PubMedQA](https://pubmedqa.github.io/) items in `data/items/A_evidence.jsonl`; SimpleQA-style items in `data/items/B_fact.jsonl`, derived from [SimpleQA](https://github.com/openai/simple-evals).
- **Artifacts:** conversations in `results/raw/`, analyzed grades in `results/graded/*__seed1.jsonl`, ablation grades in `results/graded/*__explicit_confidence.jsonl`, derived metrics and figures in `figures/`, the seed-2 summary in `results/rotation_check.md`, and the two ablation summaries in `results/sanity_A_evidence__explicit_confidence.md` and `results/sanity_B_fact__explicit_confidence.md`.
- **Reproduction:** run `python3 -m backdown.analyze --in results/graded --out figures/` in the project environment. The defaults analyze the natural variant and seed 1, excluding rotation and explicit-confidence ablation files. Use `--seed 2` for the rotation check and `--variant explicit_confidence` for the ablation.
- **Provenance:** all project code was written during the sprint. Git history begins 14 November 2026, and no pre-sprint code is included.

## References

1. Apart Research. 2026. “AI x Epistemics Research Sprint,” 13–15 November 2026. Track 1 example projects: MisleadBench and FlipRate. https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15
2. Cheng, Myra, Sunny Yu, Cinoo Lee, Pranav Khadpe, Lujain Ibrahim, and Dan Jurafsky. 2025. “ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs.” *arXiv*, 2505.13995. https://arxiv.org/abs/2505.13995
3. Fanous, Aaron, Jacob Goldberg, Ank A. Agarwal, Joanna Lin, Anson Zhou, Roxana Daneshjou, and Sanmi Koyejo. 2025. “SycEval: Evaluating LLM Sycophancy.” *arXiv*, 2502.08177, version 4. https://arxiv.org/abs/2502.08177v4
4. Jin, Qiao, Bhuwan Dhingra, Zhengping Liu, William Cohen, and Xinghua Lu. 2019. “PubMedQA: A Dataset for Biomedical Research Question Answering.” *EMNLP-IJCNLP*, Association for Computational Linguistics. https://aclanthology.org/D19-1259/
5. Ren, Richard, et al. 2025. “The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems.” *arXiv*, 2503.03750; version 3 revised 2026. https://arxiv.org/abs/2503.03750v3
6. Wei, Jason, Nguyen Karina, Hyung Won Chung, Yunxin Joy Jiao, Spencer Papay, Amelia Glaese, John Schulman, and William Fedus. 2024. “Measuring Short-Form Factuality in Large Language Models.” *arXiv*, 2411.04368. https://arxiv.org/abs/2411.04368

## Appendix

### Limitations and Dual-Use / Ethical Considerations

**Measurement and scope.** Median aggregation cannot remove shared grader bias. All 204 planned human strength labels are complete across both sets and all three labelers, but they cover 48 unique conversations, with only five per set shared by all labelers. These comparisons are limited by sample size, selection, and repeated turns. The inter-human comparisons cover 45 pairs per set in 5 conversations, enough for a consistency estimate but not for stable external validation. Label-to-strength mapping, claim orientation, and correctness definitions require sensitivity checks. English biomedical abstracts and heterogeneous trivia do not represent all factual or advisory interactions.

**Fact limits.** Fact overselling conditions on wrong answers, so each cell rests on 51 to 71 conversations rather than all 80. The items are a small, heterogeneous convenience set, and the warranted-evidence turn is a single checkable fact. Mistral's Fact runs changed router host between seeds, which confounds its rotation comparison. These features limit cross-domain and cross-provider generalization.

**Ablation limits.** The explicit-confidence experiments are plain-condition only, use 80 conversations per model per set, have two graders rather than three, and report simple means without bootstrap intervals. The confidence extractor requires a percentage adjacent to the word “confidence” and misses 10% to 19% of Evidence replies. The Fact Mistral ablation also mixes a prompt change with a router-host change. These results are manipulation checks, not headline estimates.

**Operational limits.** Hosted aliases and routes can change. Requested/returned model identifiers, timestamps, and routes are recorded, but future calls may differ. Across the analyzed Evidence records, 28 of 1,920 subject turns ended with `finish_reason=length`; across Fact records, 2 of 1,920 did. These turns remain included. Source: `turn_meta` in the graded JSONL files, also summarized in `figures/caveats.md`. Truncation may affect judged claim strength.

**Dual use and privacy.** Pushback templates could be repurposed to pressure assistants toward unsupported positions. Their intended use is auditing susceptibility and evidence responsiveness, not optimizing manipulation. Study inputs are published abstracts and constructed factual and decision scenarios; no participant personal data were collected for these API experiments. Medical examples do not establish clinical safety.

**Audit trail.** The abstract's ranges summarize Tables 1 and 2; its ablation statement summarizes Tables 5 and 6; its rotation statement summarizes `results/rotation_check.md`; its reliability figures summarize Table 3; and its human figures summarize Table 4. All metric-row identifiers are specified in their captions or adjacent text. Grader disagreements are enumerated in `figures/grader_disagreements.csv`. Conclusions remain provisional given the small, partly overlapping human sample and the uncomputed correctness-sensitivity analysis.

## LLM Usage Statement

Claude Fable 5.2 and GPT-6 Astra assisted with drafting and checking this report. Claude Haiku and the other models listed in §3.2 were used in the experiments and in checking. Repository documentation describes agent-assisted implementation of the harness and analysis. For this draft, metric values and confidence intervals were reproduced from logged graded records, and cited paper titles, authors, and URLs were checked against primary sources. The authors' 204 human strength labels (Harshil, Daksh, and Kartik, both sets) were read for the comparison, and the human–grader and inter-human estimates were taken from the regenerated `figures/grader_agreement.md`. The human label set is complete, with no strength rows blank. The authors are responsible for final review and affiliation confirmation; this statement does not imply independent human verification.
