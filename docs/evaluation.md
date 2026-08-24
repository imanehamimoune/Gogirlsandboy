# Evaluation

## Evaluation Objective

The evaluation examines the results produced by the publisher-scoring framework and assesses whether they provide a meaningful basis for identifying attractive publisher candidates.

The evaluation focuses on three questions:

1. Which publishers achieve the highest overall scores under the baseline scoring model?
2. What performance characteristics distinguish the highest-ranked feasible candidates?
3. How sensitive are publisher scores to reasonable changes in the four top-level dimension weights?

The quantitative ranking is treated as a **screening and prioritization mechanism rather than a final investment decision**. Factors such as ownership structure, valuation, strategic fit, platform compatibility, and transaction feasibility require additional assessment after the quantitative analysis.

## Publisher Population

The publisher-level feature construction initially identified **46,239 publishers** from the available game-level observations. Publishers represented by fewer than 10 games were excluded to reduce the influence of highly unstable portfolio averages. After applying this criterion, **814 publishers** remained for scoring.

A total of 49,738 game records, corresponding to 35.5% of the master dataset, could not be included in publisher-level aggregation because `publisher_primary` was unavailable.

The resulting publisher-feature dataset contained one observation per eligible publisher, with no duplicate publisher identifiers or infinite numerical values.

## Baseline Scoring Results

The four performance dimensions were combined using the baseline weighting of **35% Scale & Reach, 30% Quality, 20% Engagement, and 15% Growth & Momentum**.

Of the 814 eligible publishers, **24 received no overall score** because information required for the Quality dimension was unavailable. Missing dimension scores were not imputed or compensated for through redistribution of the remaining weights.

The ten highest-scoring publishers with complete scores were:

| Rank | Publisher                  | Overall Score |
| ---: | -------------------------- | ------------: |
|    1 | Valve                      |         0.783 |
|    2 | Coffee Stain Publishing    |         0.767 |
|    3 | PlayStation Publishing LLC |         0.764 |
|    4 | CAPCOM Co., Ltd.           |         0.740 |
|    5 | Bandai Namco Entertainment |         0.720 |
|    6 | Xbox Game Studios          |         0.711 |
|    7 | Hooded Horse               |         0.710 |
|    8 | Electronic Arts            |         0.706 |
|    9 | Klei Entertainment         |         0.698 |
|   10 | Raw Fury                   |         0.686 |

Valve achieved the highest overall score at **0.783**, followed relatively closely by Coffee Stain Publishing at **0.767** and PlayStation Publishing LLC at **0.764**. CAPCOM Co., Ltd. followed with a score of **0.740**.

The relatively small differences between several highly ranked publishers reinforce the importance of interpreting the ranking together with the individual dimension scores and sensitivity analysis rather than treating small numerical differences as absolute differences in publisher attractiveness.

## Performance of the Leading Publishers

### Valve

Valve achieved the highest overall score at **0.783**. Its dimension scores were:

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.916 |
| Quality           | 0.916 |
| Engagement        | 0.939 |
| Growth & Momentum | 0.000 |

Valve therefore performed particularly strongly in Scale & Reach, Quality, and Engagement. Its overall first-place ranking was achieved despite receiving a Growth & Momentum score of zero under the defined recent-release methodology.

This result illustrates an important characteristic of the weighted model: exceptional performance across the more heavily weighted dimensions can compensate for weakness in a lower-weighted dimension.

### Coffee Stain Publishing

Coffee Stain Publishing ranked second with an overall score of **0.767**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.743 |
| Quality           | 0.919 |
| Engagement        | 0.966 |
| Growth & Momentum | 0.253 |

Coffee Stain performed particularly strongly in Quality and Engagement. Compared with Valve, it had lower Scale & Reach but greater Growth & Momentum.

Its high ranking therefore reflects comparatively balanced performance across the four dimensions, with particularly strong player reception and continued engagement.

### PlayStation Publishing LLC

PlayStation Publishing LLC ranked third with an overall score of **0.764**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.736 |
| Quality           | 0.837 |
| Engagement        | 0.975 |
| Growth & Momentum | 0.405 |

Although quantitatively attractive, PlayStation Publishing LLC was excluded from the actionable shortlist because it is owned by a direct competitor and therefore does not represent a realistic external acquisition or partnership candidate within the project's decision context.

### CAPCOM Co., Ltd.

CAPCOM ranked fourth overall with a score of **0.740**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.658 |
| Quality           | 0.835 |
| Engagement        | 0.990 |
| Growth & Momentum | 0.409 |

CAPCOM showed particularly strong Engagement and comparatively strong Growth & Momentum. Its profile therefore differs from Valve, whose ranking is driven more strongly by Scale & Reach and Quality.

## Candidate Shortlist

The quantitative ranking was combined with a basic feasibility screen to identify candidates suitable for further strategic consideration.

PlayStation Publishing LLC was excluded because it is competitor-owned. Xbox Game Studios was also excluded from external candidate consideration because it is already part of Microsoft.

Following these feasibility exclusions, the three highest-ranked candidates were:

| Baseline Rank | Candidate               | Overall Score |
| ------------: | ----------------------- | ------------: |
|             1 | Valve                   |         0.783 |
|             2 | Coffee Stain Publishing |         0.767 |
|             4 | CAPCOM Co., Ltd.        |         0.740 |

The shortlist was intentionally limited to three candidates to create a focused set for subsequent strategic and financial assessment. The Top 3 should therefore be interpreted as a practical screening decision rather than as evidence that exactly three publishers are objectively attractive.

The candidates also provide different performance profiles. Valve is characterized by particularly strong Scale & Reach and Quality, Coffee Stain Publishing by strong Quality and Engagement, and CAPCOM by very strong Engagement together with comparatively strong Growth & Momentum.

## Score Sensitivity Analysis

Because the baseline top-level weights represent analytical judgments, a sensitivity analysis was conducted to determine how strongly publisher scores depend on those assumptions.

Each dimension was allowed to vary by ±10 percentage points around its baseline value in increments of 5 percentage points:

| Dimension         | Baseline | Tested Range |
| ----------------- | -------: | -----------: |
| Scale & Reach     |      35% |       25–45% |
| Quality           |      30% |       20–40% |
| Engagement        |      20% |       10–30% |
| Growth & Momentum |      15% |        5–25% |

The complete grid contained **625 candidate weight combinations**. After retaining only combinations whose four weights summed to 100%, **85 valid scenarios** remained.

All 85 scenarios satisfied the predefined weight constraints, no duplicate combinations were present, and the baseline 35% / 30% / 20% / 15% combination occurred exactly once.

## Score Robustness of the Baseline Top 10

For each of the baseline Top 10 publishers, the minimum and maximum overall scores across the 85 valid weighting scenarios were compared with the baseline score.

| Publisher                  | Minimum | Baseline | Maximum |
| -------------------------- | ------: | -------: | ------: |
| Valve                      |   0.689 |    0.783 |   0.877 |
| Coffee Stain Publishing    |   0.678 |    0.767 |   0.856 |
| PlayStation Publishing LLC |   0.697 |    0.764 |   0.832 |
| CAPCOM Co., Ltd.           |   0.664 |    0.740 |   0.816 |
| Bandai Namco Entertainment |   0.642 |    0.720 |   0.797 |
| Xbox Game Studios          |   0.619 |    0.711 |   0.802 |
| Hooded Horse               |   0.632 |    0.710 |   0.789 |
| Electronic Arts            |   0.636 |    0.706 |   0.777 |
| Klei Entertainment         |   0.584 |    0.698 |   0.813 |
| Raw Fury                   |   0.598 |    0.686 |   0.774 |

The results show that publisher scores are meaningfully affected by the weighting assumptions. This is expected because publishers have different strengths across the four performance dimensions.

Valve's score, for example, ranged from approximately **0.689 to 0.877**, while Coffee Stain Publishing ranged from approximately **0.678 to 0.856**. CAPCOM ranged from approximately **0.664 to 0.816**.

Klei Entertainment displayed one of the wider score ranges among the baseline Top 10, ranging from approximately **0.584 to 0.813**. This suggests that its quantitative attractiveness is comparatively sensitive to the importance assigned to the different performance dimensions.

The existence of these ranges demonstrates why the exact baseline score should not be interpreted as an absolute measure of publisher attractiveness. Instead, the baseline score represents performance under one explicitly defined set of weighting assumptions.

## Interpretation of the Shortlisted Candidates Under Alternative Weights

All three shortlisted candidates exhibited changes in overall score when the top-level dimension weights were varied.

Valve's baseline score of **0.783** varied between **0.689 and 0.877**. This comparatively broad range is consistent with its uneven dimension profile: Valve performs exceptionally strongly in Scale & Reach, Quality, and Engagement but has a Growth & Momentum score of zero. Increasing or decreasing the relative importance of these dimensions therefore changes its overall score.

Coffee Stain Publishing varied between **0.678 and 0.856**, compared with its baseline score of **0.767**. Its strong Quality and Engagement performance supports its overall score across different assumptions, although the exact result remains sensitive to the relative dimension weights.

CAPCOM's baseline score of **0.740** varied between **0.664 and 0.816**. Its strong Engagement and Growth & Momentum performance means that scenarios assigning greater importance to these dimensions can improve its relative assessment.

The sensitivity analysis therefore supports interpreting the three candidates as publishers with different strategic performance profiles rather than treating the baseline ranking positions as fixed or universally optimal.

## Limits of the Current Sensitivity Evaluation

The executed sensitivity output provides evidence about **score sensitivity**, but the available results do not yet provide the full numerical evidence required to evaluate **ranking robustness**.

In particular, the current output reports the minimum, baseline, and maximum scores across 85 valid weighting scenarios, but does not report:

* mean absolute rank change;
* Spearman rank correlation with the baseline;
* Top-5, Top-10, or Top-20 overlap;
* minimum and maximum rank by publisher;
* Top-N appearance frequencies.

Consequently, the current sensitivity results demonstrate how much the **numerical scores** can change under alternative weights, but they are not sufficient on their own to conclude that the **publisher ranking itself is robust**.

For example, Valve's score may change substantially while it remains ranked first or close to first in most scenarios. Conversely, a publisher's score may change relatively little while its rank changes considerably if several publishers have similar scores.

A complete assessment of ranking robustness should therefore incorporate the ranking-stability measures described in the methodology.

## Validation Results

The publisher-feature construction and scoring procedures passed several internal validation checks.

The final publisher-level feature dataset contained **814 unique publishers**, all meeting the minimum portfolio-size requirement. No duplicate publishers or infinite numerical values were identified, and all normalized variables fell within the expected 0–1 range.

Missingness was limited primarily to `review_score` (**2.95%**) and `avg_positive_review_ratio` (**0.25%**). This resulted in **24 publishers** receiving a missing Quality score and therefore a missing overall score. No missing dimension scores occurred for Scale & Reach, Engagement, or Growth & Momentum.

All non-missing dimension and overall scores remained within the expected 0–1 range.

The sensitivity procedure generated **625 candidate weighting combinations**, of which **85** satisfied the requirement that the four weights sum to 100%. The valid scenarios contained no duplicate weighting combinations, and the baseline scenario was represented exactly once.

## Overall Evaluation

The scoring framework reduced the eligible publisher population to a transparent ranking based on four complementary dimensions of performance.

Under the baseline weighting scheme, **Valve ranked first with an overall score of 0.783, Coffee Stain Publishing second with 0.767, and PlayStation Publishing LLC third with 0.764**. After applying the feasibility screen, **Valve, Coffee Stain Publishing, and CAPCOM** formed the three-candidate shortlist.

The shortlisted publishers reached high overall scores through different combinations of strengths. Valve performed particularly strongly in Scale & Reach and Quality, Coffee Stain Publishing combined strong Quality with high Engagement, and CAPCOM combined very high Engagement with comparatively strong Growth & Momentum.

The sensitivity analysis confirms that the numerical scores depend meaningfully on the selected top-level weights. Across the 85 valid alternative weighting scenarios, the shortlisted publishers experienced non-trivial score ranges. This reinforces the importance of treating the baseline scores as decision-support indicators rather than precise or absolute measures of publisher value.

Based on the currently available sensitivity output, the analysis supports the identification of strong quantitative candidates but does **not yet establish full ranking robustness**. A stronger robustness conclusion requires evaluation of rank changes, Spearman rank correlations, and Top-N retention across the alternative scenarios.

The final shortlist should therefore be interpreted as a **quantitative screening result for subsequent due diligence**. Strategic fit, ownership structure, transaction feasibility, platform suitability, valuation, and expected financial returns remain necessary considerations before any investment or partnership recommendation is made.
