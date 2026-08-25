# Evaluation

## Evaluation Objective

The evaluation examines the results produced by the publisher-scoring framework and assesses whether they provide a meaningful basis for identifying attractive publisher candidates.

The evaluation addresses three questions:

1. Which publishers achieve the highest overall scores under the baseline scoring model?
2. What performance characteristics distinguish the highest-ranked feasible candidates?
3. How sensitive are publisher scores to reasonable changes in the four top-level dimension weights?

The quantitative ranking is treated as a **screening and prioritization mechanism rather than a final investment decision**.

Factors such as ownership structure, valuation, strategic fit, platform compatibility, and transaction feasibility require additional assessment after the quantitative analysis.

---

## Publisher Population

The publisher-level feature construction initially identified **46,239 publishers** from the available game-level observations.

The analysis was intended to evaluate **established publishers represented by at least 10 games in the dataset**, rather than publishers whose observed performance was based on only a small number of titles.

Publishers represented by fewer than 10 games were therefore excluded because their portfolio-level averages may be highly sensitive to the performance of individual games.

### Eligible Publishers

After applying the minimum portfolio-size criterion:

* **814 publishers** remained eligible for scoring.
* **24 publishers** could not receive an overall score because information required for the Quality dimension was unavailable.
* **790 publishers** therefore received complete overall scores.

A total of **49,738 game records**, corresponding to **35.5% of the master dataset**, could not be included in publisher-level aggregation because `publisher_primary` was unavailable.

### Validation

The resulting publisher-feature dataset:

* contained one observation per eligible publisher;
* contained no duplicate publisher identifiers; and
* contained no infinite numerical values.

---

## Baseline Scoring Results

The four performance dimensions were combined using the baseline weighting:

| Dimension         |   Weight |
| ----------------- | -------: |
| Scale & Reach     |      35% |
| Quality           |      30% |
| Engagement        |      20% |
| Growth & Momentum |      15% |
| **Total**         | **100%** |

Missing dimension scores were not imputed or compensated for by redistributing their weights across the remaining dimensions.

### Baseline Top 10

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

Valve achieved the highest overall score at **0.783**, followed by Coffee Stain Publishing at **0.767** and PlayStation Publishing LLC at **0.764**. CAPCOM Co., Ltd. followed with an overall score of **0.740**.

### Interpretation

Several publishers in the upper part of the ranking are separated by relatively small score differences:

* Valve leads Coffee Stain Publishing by approximately **0.016 points**.
* Coffee Stain Publishing and PlayStation Publishing LLC differ by approximately **0.003 points**.
* Xbox Game Studios and Hooded Horse are separated by less than **0.001 points**.

These small differences indicate that the exact ordering of closely positioned publishers should not be overinterpreted.

The overall score is more useful for identifying a group of quantitatively strong publishers than for implying that small differences between adjacent positions represent substantial differences in publisher attractiveness.

The highest-ranked publishers are also not simply those that dominate one individual performance dimension. The overall ranking instead rewards publishers that combine competitive performance across several dimensions.

---

## Individual Dimension Results

Examining the four dimensions separately provides additional insight into the performance profiles underlying the overall ranking.

### Scale & Reach

Valve achieved the highest Scale & Reach score at **0.916**, substantially ahead of Coffee Stain Publishing at **0.743** and PlayStation Publishing LLC at **0.736**.

CAPCOM Co., Ltd. also appeared among the ten strongest publishers in this dimension with a score of **0.658**.

Valve's substantial advantage in Scale & Reach contributed strongly to its first-place overall ranking. It combined the strongest Scale & Reach result with high Quality and Engagement scores.

### Quality

The three highest Quality scores were:

| Publisher             | Quality Score |
| --------------------- | ------------: |
| New Blood Interactive |         0.972 |
| HIKARI FIELD          |         0.968 |
| Adamvision Studios    |         0.966 |

None of these publishers appeared among the highest overall-ranked publishers, illustrating that strong player reception alone does not determine the final ranking.

Among the shortlisted candidates:

* Coffee Stain Publishing achieved a Quality score of **0.919**;
* Valve achieved **0.916**; and
* CAPCOM achieved **0.835**.

### Engagement

Engagement scores were particularly high among several publishers.

Crytivo achieved the maximum normalized Engagement score of **1.000**, while several other publishers scored close to this upper boundary.

Among the leading candidates:

| Publisher               | Engagement Score |
| ----------------------- | ---------------: |
| CAPCOM Co., Ltd.        |            0.990 |
| Coffee Stain Publishing |            0.966 |
| Valve                   |            0.939 |

Because Engagement is normalized using percentile ranks, these values represent publishers' **relative positions within the eligible publisher population**, rather than literal percentages of owners who remain active.

The concentration of leading Engagement scores near 1.0 is therefore expected and should not be interpreted as indicating active-user rates of approximately 99–100%.

### Growth & Momentum

The publishers leading Growth & Momentum differed substantially from those leading the overall ranking.

| Publisher         | Growth & Momentum Score |
| ----------------- | ----------------------: |
| Inspector Studios |                   0.905 |
| STuNT             |                   0.889 |
| 072 Project       |                   0.874 |

None of these publishers appeared in the baseline overall Top 10.

Valve provides a contrasting example. Despite ranking first overall, Valve received a Growth & Momentum score of **0.000**. Its first-place position was therefore driven by exceptionally strong performance in Scale & Reach, Quality, and Engagement rather than recent release activity.

---

## Performance of the Leading Publishers

### Valve

Valve achieved the highest overall score at **0.783**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.916 |
| Quality           | 0.916 |
| Engagement        | 0.939 |
| Growth & Momentum | 0.000 |

Valve performed particularly strongly in Scale & Reach, Quality, and Engagement.

Valve's Growth & Momentum score of **0.000** results from the release-date-based definition used by the model. No Valve title with an available release date falls within the defined two-year recent-release window. However, this measure may understate Valve's current development activity because some actively maintained or relaunched titles have missing release dates in the dataset. The implications of this data limitation are discussed further in `limitations.md`.

Consequently, both `recent_release_ratio` and `recent_release_count_norm`, the two components of the Growth & Momentum dimension, are zero.

Under the methodology's definition of a recent release, none of Valve's observed games therefore fell within the two-year recent-release window.

Its first-place overall ranking was achieved despite this result because of its exceptionally strong performance across the other three dimensions.

This illustrates an important characteristic of the weighted model: strong performance across the more heavily weighted dimensions can compensate for weakness in a lower-weighted dimension. It also highlights why the individual dimension scores should be examined alongside the overall ranking.

### Coffee Stain Publishing

Coffee Stain Publishing ranked second with an overall score of **0.767**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.743 |
| Quality           | 0.919 |
| Engagement        | 0.966 |
| Growth & Momentum | 0.253 |

Coffee Stain Publishing performed particularly strongly in Quality and Engagement.

Compared with Valve, it achieved lower Scale & Reach but greater Growth & Momentum. Its high ranking therefore reflects comparatively balanced performance across the dimensions, with particularly strong player reception and continued engagement.

### PlayStation Publishing LLC

PlayStation Publishing LLC ranked third with an overall score of **0.764**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.736 |
| Quality           | 0.837 |
| Engagement        | 0.975 |
| Growth & Momentum | 0.405 |

Although quantitatively attractive, PlayStation Publishing LLC was excluded from the actionable shortlist because it forms part of Sony's first-party publishing activities.

As a direct competitor-owned publisher, it was not considered a realistic external acquisition or partnership candidate within the scope of the project.

### CAPCOM Co., Ltd.

CAPCOM ranked fourth overall with a score of **0.740**.

| Dimension         | Score |
| ----------------- | ----: |
| Scale & Reach     | 0.658 |
| Quality           | 0.835 |
| Engagement        | 0.990 |
| Growth & Momentum | 0.409 |

CAPCOM demonstrated particularly strong Engagement and comparatively strong Growth & Momentum.

Its performance profile therefore differs from Valve, whose overall position is driven more strongly by Scale & Reach and Quality.

---

## Candidate Shortlist and Feasibility Screening

The quantitative ranking was used as an initial screening mechanism and was subsequently combined with a strategic feasibility assessment.

A high quantitative score was therefore considered evidence that a publisher warranted further investigation, but did not automatically imply that an acquisition was realistic or that acquisition was the most appropriate form of cooperation.

### Excluded Candidates

Two highly ranked publishers were excluded from the actionable external shortlist for strategic reasons.

**PlayStation Publishing LLC** is part of Sony's first-party publishing activities and therefore belongs to a direct platform competitor.

The competitive relationship between Microsoft and Sony, including tensions surrounding Microsoft's acquisition of Activision Blizzard and concerns over the future platform availability of major franchises such as *Call of Duty*, was considered to make PlayStation Publishing an unsuitable partnership or acquisition candidate within the scope of the project.

**Xbox Game Studios** is already part of Microsoft and therefore does not represent an external investment, acquisition, or partnership opportunity.

Its quantitative performance can nevertheless serve as an internal reference point when comparing external candidates with Microsoft's existing publishing activities.

### Actionable Shortlist

After applying these feasibility considerations, the three highest-ranked external candidates were:

| Baseline Rank | Candidate               | Overall Score |
| ------------: | ----------------------- | ------------: |
|             1 | Valve                   |         0.783 |
|             2 | Coffee Stain Publishing |         0.767 |
|             4 | CAPCOM Co., Ltd.        |         0.740 |

The shortlist was intentionally limited to three candidates.

The purpose was to reduce the quantitative ranking to a manageable number of candidates for deeper strategic and financial due diligence, rather than to establish three as a statistically determined cutoff.

Publishers immediately below the shortlist should therefore not automatically be interpreted as unattractive.

### Strategic Feasibility of the Shortlisted Candidates

The three shortlisted publishers differ not only in their quantitative performance profiles but also in the type of strategic relationship considered realistic.

#### Valve

Valve is a major industry player and is privately held, making an acquisition particularly difficult.

Its quantitative profile nevertheless makes it strategically attractive, with exceptional Scale & Reach, Quality, and Engagement. At the same time, its zero Growth & Momentum score identifies an area in which cooperation with Microsoft could offer complementary value.

Within the project, Valve is therefore considered a **strategic partnership candidate rather than an acquisition target**.

A potential area of cooperation is Microsoft's Game Pass model, provided that a partnership can create sufficient value for Valve as well as Microsoft.

#### Coffee Stain Publishing

Coffee Stain Publishing combines a high quantitative ranking with a more manageable acquisition profile.

Unlike Valve, the project considers a full acquisition to be a realistic strategic option provided that sufficient acquisition capital is available.

Its strong Quality and Engagement scores make it relevant as a candidate for deeper financial and strategic due diligence.

#### CAPCOM Co., Ltd.

CAPCOM also performs strongly in the quantitative assessment, especially in Engagement and Growth & Momentum.

However, its size makes a complete acquisition more capital-intensive.

The project therefore considers a **minority investment or strategic partnership** more realistic than full ownership.

Potential cooperation could include joint marketing activities, publishing arrangements, and broader availability of selected games across Microsoft's ecosystem.

### Feasibility Interpretation

The feasibility assessment does not remove publishers from the quantitative ranking.

Instead, it translates quantitative attractiveness into different potential strategic actions:

| Candidate               | Potential Strategic Action                   |
| ----------------------- | -------------------------------------------- |
| Valve                   | Strategic partnership                        |
| Coffee Stain Publishing | Potential acquisition                        |
| CAPCOM Co., Ltd.        | Minority investment or strategic partnership |

---

## Score Sensitivity Analysis

Because the baseline top-level weights represent analytical judgments rather than objectively determined values, a sensitivity analysis was conducted to determine how strongly publisher scores depend on those assumptions.

### Weight Scenarios

Each dimension was allowed to vary by ±10 percentage points around its baseline value in increments of 5 percentage points:

| Dimension         | Baseline | Tested Range |
| ----------------- | -------: | -----------: |
| Scale & Reach     |      35% |       25–45% |
| Quality           |      30% |       20–40% |
| Engagement        |      20% |       10–30% |
| Growth & Momentum |      15% |        5–25% |

The complete grid contained **625 candidate weight combinations**.

After retaining only combinations whose four weights summed to 100%, **85 valid scenarios** remained.

All 85 scenarios:

* satisfied the predefined weight constraints;
* contained no duplicate combinations; and
* included the baseline weighting of 35% / 30% / 20% / 15% exactly once.

The baseline Top 10 publishers were selected **before** the sensitivity results were examined.

For each of these publishers, the minimum and maximum overall scores across the 85 valid scenarios were compared with the original baseline score.

---

## Score Sensitivity of the Baseline Top 10

The resulting score ranges were:

| Publisher                  | Minimum | Baseline | Maximum | Approx. Range |
| -------------------------- | ------: | -------: | ------: | ------------: |
| Valve                      |   0.689 |    0.783 |   0.877 |         0.188 |
| Coffee Stain Publishing    |   0.678 |    0.767 |   0.856 |         0.178 |
| PlayStation Publishing LLC |   0.697 |    0.764 |   0.832 |         0.135 |
| CAPCOM Co., Ltd.           |   0.664 |    0.740 |   0.816 |         0.152 |
| Bandai Namco Entertainment |   0.642 |    0.720 |   0.797 |         0.155 |
| Xbox Game Studios          |   0.619 |    0.711 |   0.802 |         0.183 |
| Hooded Horse               |   0.632 |    0.710 |   0.789 |         0.157 |
| Electronic Arts            |   0.636 |    0.706 |   0.777 |         0.141 |
| Klei Entertainment         |   0.584 |    0.698 |   0.813 |         0.230 |
| Raw Fury                   |   0.598 |    0.686 |   0.774 |         0.176 |

### Interpretation

Publisher scores are meaningfully affected by the top-level weighting assumptions because publishers have different strengths across the four performance dimensions.

Among the baseline Top 10:

* **Klei Entertainment** exhibited the widest score range at approximately **0.230**.
* **Valve** followed with approximately **0.188**.
* **Xbox Game Studios** showed a range of approximately **0.183**.

The narrowest ranges were observed for:

* **PlayStation Publishing LLC:** approximately **0.135**;
* **Electronic Arts:** approximately **0.141**; and
* **CAPCOM:** approximately **0.152**.

A wider range indicates that a publisher's overall numerical assessment is more responsive to changes in the relative importance assigned to the four dimensions. It does **not** necessarily indicate weaker performance.

Valve provides a clear example. Its combination of very strong Scale & Reach, Quality, and Engagement with a Growth & Momentum score of zero creates an uneven performance profile, making its overall score comparatively responsive to changes in the top-level weights.

CAPCOM's narrower score range indicates that its numerical score is somewhat less sensitive to the tested weighting assumptions.

---

## Overlapping Score Ranges

The sensitivity ranges overlap among the baseline Top 10 publishers.

For example:

| Publisher                  | Tested Score Range |
| -------------------------- | -----------------: |
| Valve                      |        0.689–0.877 |
| Coffee Stain Publishing    |        0.678–0.856 |
| PlayStation Publishing LLC |        0.697–0.832 |
| CAPCOM Co., Ltd.           |        0.664–0.816 |

Valve has the highest baseline score, but its tested range overlaps with those of Coffee Stain Publishing, PlayStation Publishing LLC, and CAPCOM.

This overlap indicates that the differences between baseline scores are relatively small compared with the score changes that can result from alternative weighting assumptions. The baseline ordering should therefore not be interpreted as evidence that one publisher is unambiguously superior to another under every reasonable set of priorities.

However, overlapping score ranges do **not** demonstrate that publishers actually exchange ranking positions under the same weighting scenario. A publisher's minimum and another publisher's maximum may occur under different combinations of weights.

The ranges therefore provide evidence of **score sensitivity rather than ranking instability**.

---

## Shortlisted Candidates Under Alternative Weights

The three shortlisted candidates all experienced changes in their overall scores when the top-level dimension weights were varied:

| Candidate               | Minimum | Baseline | Maximum | Approx. Range |
| ----------------------- | ------: | -------: | ------: | ------------: |
| Valve                   |   0.689 |    0.783 |   0.877 |         0.188 |
| Coffee Stain Publishing |   0.678 |    0.767 |   0.856 |         0.178 |
| CAPCOM Co., Ltd.        |   0.664 |    0.740 |   0.816 |         0.152 |

Valve's comparatively broad range is consistent with its uneven dimension profile.

Coffee Stain Publishing's strong Quality and Engagement performance supports its assessment across different assumptions, although its exact score remains sensitive to the relative dimension weights.

CAPCOM's score range is somewhat narrower than those of Valve and Coffee Stain Publishing. Its strong Engagement and Growth & Momentum also mean that its assessment benefits relatively more when these dimensions receive greater emphasis.

The sensitivity results therefore reinforce the interpretation of the three candidates as publishers with different performance profiles rather than treating the exact baseline score differences as fixed measures of relative attractiveness.

---

## Limits of the Sensitivity Evaluation

The sensitivity analysis evaluates **score sensitivity only**.

It measures the minimum and maximum scores obtained by the baseline Top 10 publishers across alternative top-level weighting combinations, but it does not recalculate or analyze changes in publisher ranking positions.

The analysis therefore does **not** measure:

* rank changes under alternative weights;
* rank correlation with the baseline ranking;
* changes in Top-5 or Top-10 membership; or
* the frequency with which individual publishers retain a particular ranking position.

Consequently, the current results cannot establish whether the publisher ranking itself is robust to alternative weighting assumptions.

For example, Valve's numerical score changes substantially across the tested scenarios, but this does not establish whether it remains first, moves several positions, or is overtaken by another publisher. Conversely, a publisher with a relatively narrow score range could still experience ranking changes if several competing publishers have similar scores.

A separate ranking-sensitivity analysis would be required to determine whether alternative weighting assumptions materially change publisher positions or shortlist membership.

This was outside the scope of the present sensitivity analysis.

---

## Validation Results

The publisher-feature construction, scoring procedure, and sensitivity analysis included several internal validation checks.

### Publisher-Feature Validation

The final publisher-level feature dataset contained **814 unique publishers**, all meeting the minimum portfolio-size requirement.

The validation identified:

* no duplicate publisher identifiers;
* no infinite numerical values; and
* no normalized variables outside the expected 0–1 range.

### Missingness

Missingness was limited primarily to:

| Variable                    | Missing |
| --------------------------- | ------: |
| `review_score`              |   2.95% |
| `avg_positive_review_ratio` |   0.25% |

This resulted in **24 publishers** receiving a missing Quality score and therefore a missing overall score.

No missing dimension scores occurred for Scale & Reach, Engagement, or Growth & Momentum.

All non-missing dimension scores and overall scores remained within the expected 0–1 range.

### Sensitivity Validation

The sensitivity procedure generated:

* **625 candidate weighting combinations**;
* **85 valid combinations** whose four weights summed to 100%;
* no duplicate valid weighting combinations; and
* exactly one occurrence of the baseline scenario.

The baseline scores of all Top 10 publishers also fell between their calculated minimum and maximum sensitivity scores, providing an additional consistency check on the scenario calculations.

---

## Overall Evaluation

The scoring framework reduced a large publisher universe to a transparent ranking based on four complementary dimensions of performance.

Under the baseline weighting scheme:

1. **Valve** ranked first with an overall score of **0.783**.
2. **Coffee Stain Publishing** ranked second with **0.767**.
3. **PlayStation Publishing LLC** ranked third with **0.764**.

After applying the feasibility screen, **Valve, Coffee Stain Publishing, and CAPCOM** formed the three-candidate shortlist.

The dimension results show that the shortlisted publishers reach their high overall scores through different combinations of strengths:

* **Valve** combines exceptional Scale & Reach with strong Quality and Engagement.
* **Coffee Stain Publishing** combines particularly strong Quality and Engagement with a comparatively balanced profile.
* **CAPCOM** combines very high Engagement with stronger recent publishing momentum.

The sensitivity analysis demonstrates that numerical publisher scores depend meaningfully on the selected top-level weights. Score ranges overlap substantially among several of the leading publishers, reinforcing the importance of treating small baseline score differences cautiously.

The sensitivity analysis evaluates **score variation rather than ranking variation** and therefore cannot establish whether the ordering or membership of the highest-ranked publishers remains stable across alternative weighting scenarios.

The final shortlist should consequently be interpreted as a **quantitative screening result for subsequent due diligence rather than a definitive investment recommendation**.

The scoring framework identifies publishers that warrant further investigation, while strategic fit, ownership structure, transaction feasibility, platform suitability, valuation, and expected financial returns remain necessary considerations before determining an appropriate acquisition, investment, or partnership strategy.
