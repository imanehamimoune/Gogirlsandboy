# Methodology

## Analytical Objective

The analysis aimed to identify and compare high-performing publishers using a quantitative scoring framework. Publishers were assessed across four dimensions: **Scale & Reach, Quality, Engagement, and Growth & Momentum**.

Scale & Reach captures the size and accessibility of a publisher's audience, while Quality represents how positively its games are received by players. Engagement complements these measures by capturing ongoing player activity rather than accumulated reach alone. Finally, Growth & Momentum reflects recent publishing activity and therefore provides an indication of current portfolio development rather than historical performance only. Together, the four dimensions gives us insight into a publisher's performance: market presence, product reception, player activity, and recent publishing activity.

The analysis was conducted at the publisher level. Game-level information was aggregated into publisher-level features before the scoring procedure was applied. The resulting publisher scores were used to rank publishers according to their overall performance across the four dimensions.

## Publisher-Level Features

The scoring procedure used a set of publisher-level features representing the four performance dimensions. Where necessary, features were normalized to a common 0–1 scale before being combined so that variables measured on different scales could contribute to the same score.

### Scale & Reach

Scale & Reach was designed to represent the size of a publisher's audience and the breadth of its accessibility. It consisted of:

* `avg_owners_mid_norm`, representing normalized average estimated ownership;
* `avg_language_count_norm`, representing normalized average language availability.

Within the dimension, estimated ownership received a weight of **80%**, while language availability received **20%**.

The resulting dimension score was calculated as:

`Scale & Reach = 0.80 × avg_owners_mid_norm + 0.20 × avg_language_count_norm`

### Quality

Quality was represented using two measures:

* `review_score_norm`, a normalized version of the publisher-level review score;
* `avg_positive_review_ratio`, representing the average proportion of positive reviews.

The original review score was retained in its interpretable form in the publisher-feature dataset and was min-max normalized to the 0–1 range only when constructing the Quality score. The two quality measures were assigned equal weights.

The dimension was therefore calculated as:

`Quality = 0.50 × review_score_norm + 0.50 × avg_positive_review_ratio`

### Engagement

Engagement was represented by `avg_active_users_rate_norm`, which captures the normalized average active-user rate.

Because Engagement was represented by a single feature, no additional within-dimension weighting was required:

`Engagement = avg_active_users_rate_norm`

### Growth & Momentum

Growth & Momentum was designed to capture recent publishing activity rather than total historical portfolio size. It consisted of:

* `recent_release_ratio`, representing the proportion of a publisher's portfolio classified as recent releases;
* `recent_release_count_norm`, representing the normalized number of recent releases.

The recent-release ratio received a weight of **60%**, while the normalized recent-release count received **40%**:

`Growth & Momentum = 0.60 × recent_release_ratio + 0.40 × recent_release_count_norm`

Using recent releases rather than total game count was intended to make this dimension reflect current publishing momentum rather than publisher size.

## Overall Publisher Score

The four dimension scores were combined into a single overall publisher score using a weighted additive scoring model.

The baseline dimension weights were:

| Dimension         |   Weight |
| ----------------- | -------: |
| Scale & Reach     |      35% |
| Quality           |      30% |
| Engagement        |      20% |
| Growth & Momentum |      15% |
| **Total**         | **100%** |

The overall score was calculated as:

`Overall Score = 0.35 × Scale & Reach + 0.30 × Quality + 0.20 × Engagement + 0.15 × Growth & Momentum`

### Weighting Rationale

The four dimensions were assigned different weights according to their relative importance for identifying consistently high-performing publishers. **Scale & Reach received the highest weight (35%)** because the ability to reach a large player base provides an indication of a publisher's market presence and commercial scale. A publisher with substantial ownership and broad accessibility has demonstrated an ability to attract customers across a comparatively large market.

**Quality received the second-highest weight (30%)** because commercial reach alone does not necessarily indicate sustainable performance. Positive player reception provides evidence that a publisher's games meet player expectations and can contribute to customer satisfaction, reputation, and longer-term trust in the publisher.

**Engagement received a weight of 20%** to capture continued player activity after acquisition. This dimension complements Scale & Reach by distinguishing between games that have accumulated a large audience and games that continue to attract active players. It therefore supports the objective of identifying publishers with sustained performance rather than those whose success is driven primarily by isolated releases.

Finally, **Growth & Momentum received a weight of 15%** to incorporate recent publishing activity into the assessment. Although established and consistent performance was prioritized, recent activity provides additional information about whether a publisher continues to develop and expand its portfolio. The lower weight prevents recent activity from outweighing demonstrated historical performance while still rewarding publishers showing continued momentum.

The resulting baseline weighting was therefore **35% Scale & Reach, 30% Quality, 20% Engagement, and 15% Growth & Momentum**. These weights represent an analytical judgment about the relative importance of the four dimensions rather than objectively determined values. A sensitivity analysis was consequently conducted to assess whether the resulting publisher rankings remained stable under alternative weighting assumptions.

Missing dimension scores were not compensated for by redistributing their weights across the remaining dimensions. If any of the four required dimension scores was missing, the corresponding overall score was also treated as missing. This ensured that publishers were evaluated using the same scoring structure rather than being ranked using different effective weight combinations.

## Publisher Ranking

Publishers with complete overall scores were ranked in descending order, with higher overall scores indicating stronger performance according to the scoring framework.

Tied overall scores were assigned the same rank using a minimum-rank approach. Consequently, publishers with identical scores received the same highest applicable position.

The calculated dimension scores and overall scores were validated to ensure that non-missing values remained within the expected 0–1 range.

## Sensitivity Analysis

Because the overall publisher ranking depends on the weights assigned to the four performance dimensions, a sensitivity analysis was conducted to assess how strongly the results depended on the baseline weighting assumptions.

The internal composition of the four dimensions was held constant throughout this analysis. Only the four top-level dimension weights were varied. This isolated the effect of changing the relative importance assigned to Scale & Reach, Quality, Engagement, and Growth & Momentum.

### Weight Scenarios

The baseline weights were varied within the following ranges:

| Dimension         | Baseline | Tested range |
| ----------------- | -------: | -----------: |
| Scale & Reach     |      35% |       25–45% |
| Quality           |      30% |       20–40% |
| Engagement        |      20% |       10–30% |
| Growth & Momentum |      15% |        5–25% |

Weights were varied in increments of **5 percentage points**. Only combinations whose four weights summed to 100% were retained as valid scenarios.

For every valid scenario, publisher overall scores and rankings were recalculated while leaving the underlying publisher features and within-dimension weights unchanged.

### Ranking Stability

Each alternative ranking was compared with the baseline ranking using several complementary measures.

**Mean absolute rank change** measured the average magnitude of publisher movements relative to their baseline positions.

**Spearman rank correlation** measured the similarity between each scenario's complete publisher ranking and the baseline ranking. Values closer to 1 indicate that the ordering of publishers remained similar despite changes in the dimension weights.

**Top-N overlap** measured the proportion of publishers from the baseline Top 5, Top 10, and Top 20 that remained within the corresponding group under each alternative weighting scenario.

Together, these measures assessed both overall ranking stability and the stability of the publishers occupying the highest-ranked positions.

## Publisher-Level Sensitivity

Sensitivity was also assessed separately for each publisher across all valid weighting scenarios.

For each publisher, the analysis calculated the minimum, maximum, and mean overall score; score standard deviation and range; minimum and maximum rank; rank range; and mean absolute change from the baseline rank.

The proportion of valid scenarios in which each publisher appeared in the Top 5, Top 10, and Top 20 was also calculated. These measures were used to distinguish publishers whose relative performance remained stable across weighting assumptions from those whose ranking was highly dependent on the selected weights.

## Dimension-Level Sensitivity

The relationship between individual dimension weights and overall ranking stability was examined across the set of valid scenarios. For each dimension, Pearson correlations were calculated between its assigned weight and:

* mean absolute publisher rank change; and
* the Spearman correlation between the scenario ranking and baseline ranking.

These correlations were used as descriptive measures of association within the constrained weighting scenarios. They were not interpreted as causal effects because changing one dimension's weight necessarily required changes to other weights in order for the total to remain 100%.

## Representative Weighting Scenarios

In addition to the full sensitivity grid, controlled representative scenarios were constructed to provide more interpretable comparisons with the baseline model.

For each of the four dimensions, its baseline weight was increased by **10 percentage points**. The weights assigned to the other three dimensions were reduced proportionally so that their relative proportions were maintained and the total weight remained 100%.

Publisher scores and rankings were recalculated under each of these scenarios. Ranking similarity, mean absolute rank change, Top-5, Top-10, and Top-20 overlap, and changes among the highest-ranked publishers were then compared with the baseline results.

This provided an interpretable assessment of how the ranking would respond if substantially greater importance were assigned to one performance dimension at a time.

## Validation

Several validation checks were incorporated into the scoring and sensitivity procedures. The analysis verified that required publisher-level features were available, publisher identifiers were unique, and numerical inputs did not contain infinite values.

The baseline dimension scores and overall scores were reconstructed before the sensitivity analysis. Scenario weights were checked to ensure that they remained within their predefined ranges, summed to 100%, and were not duplicated. Scenario-level scores were checked to remain within the 0–1 range, and publisher rankings were independently verified against their calculated overall scores.

These checks were intended to ensure that changes observed in the sensitivity analysis resulted from the alternative weighting assumptions rather than inconsistencies in the scoring implementation.
