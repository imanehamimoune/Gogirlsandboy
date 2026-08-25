# Methodology

## Analytical Objective

The analysis aimed to identify and compare high-performing publishers using a quantitative scoring framework.

Rather than defining publisher performance using a single measure, publishers were assessed across four complementary dimensions:

| Dimension             | Purpose                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Scale & Reach**     | Represents the typical audience size and accessibility of a publisher's games                                                        |
| **Quality**           | Reflects how positively the publisher's games are received by players                                                                |
| **Engagement**        | Captures continued player activity rather than accumulated ownership alone                                                           |
| **Growth & Momentum** | Reflects recent publishing activity and whether a publisher remains active rather than relying exclusively on historical performance |

Together, these dimensions represent market reach, product reception, player activity, and recent publishing activity.

The analysis was conducted at the **publisher level**. Game-level information from the master dataset was first aggregated into publisher-level features. These features were subsequently used to construct the four dimension scores and the overall publisher ranking.

### Excluded Financial-Performance Dimension

An additional financial-performance dimension based on `est_revenue_eur` was considered but excluded from the scoring framework.

`est_revenue_eur` is an approximate proxy derived from SteamSpy ownership ranges and current prices rather than observed publisher revenue. The underlying ownership estimates are bucketed, and the calculation does not account for:

* historical pricing,
* regional pricing,
* refunds,
* bundles,
* free-to-play behavior, or
* Steam's revenue share.

The variable was therefore not considered sufficiently reliable to serve as an independent performance dimension.

---

## Publisher-Level Aggregation

The game-level master dataset was aggregated by `publisher_primary` to create one observation per publisher.

Games for which `publisher_primary` was unavailable could not be assigned to a publisher and were therefore excluded from the publisher-level aggregation rather than being assigned to an assumed publisher.

### Aggregation Approach

Publisher-level measures generally represent the **average characteristics of a publisher's games rather than portfolio totals**.

This approach was used to evaluate the typical performance of games within a publisher's portfolio while reducing the extent to which publishers with larger portfolios automatically received higher scores.

### Publisher-Level Features

Eight primary publisher-level features were constructed:

| Feature                     | Definition                                                            |
| --------------------------- | --------------------------------------------------------------------- |
| `game_count`                | Number of games associated with the publisher                         |
| `review_score`              | Mean review score across the publisher's games                        |
| `avg_owners_mid`            | Mean SteamSpy ownership midpoint across the publisher's games         |
| `avg_language_count`        | Mean number of supported languages across the publisher's games       |
| `avg_positive_review_ratio` | Mean game-level positive-review ratio                                 |
| `avg_active_users_rate`     | Mean game-level active-user rate                                      |
| `recent_release_count`      | Number of games classified as recent releases                         |
| `recent_release_ratio`      | Proportion of the publisher's portfolio classified as recent releases |

### Review Measures

Steam uses a `review_score` of `0` when insufficient reviews are available to assign a review score.

For the purpose of calculating the publisher-level mean, these values were treated as missing rather than interpreted as poor review performance. The original meaning of the game-level variable was otherwise preserved.

For each game, the positive-review ratio was calculated as:

`positive_review_ratio = positive / (positive + negative)`

The ratio was calculated only where the total number of positive and negative reviews was greater than zero. Games with no available reviews therefore received a missing ratio rather than a value of zero.

The publisher-level `avg_positive_review_ratio` was subsequently calculated as the mean of the available game-level ratios.

This gives each game equal influence on the publisher-level measure rather than allowing games with exceptionally large numbers of reviews to dominate the publisher's Quality assessment.

### Active-User Rate

For each game, the active-user rate was calculated as:

`active_user_rate = concurrent_users_yesterday / owners_mid`

The calculation was performed only where the estimated ownership midpoint was greater than zero.

A zero or unavailable denominator therefore resulted in a missing value rather than zero or an infinite value.

The game-level rates were subsequently averaged by publisher to produce `avg_active_users_rate`.

This measure was intended to capture ongoing player activity relative to estimated ownership rather than accumulated audience size alone.

### Recent Releases

A game was classified as a recent release if its release date fell within **two years of the latest release date observed in the dataset**.

The maximum observed release date was used as a fixed reference point rather than the current calendar date because the underlying data represent a fixed snapshot.

For each publisher:

* `recent_release_count` represents the number of games meeting this definition.
* `recent_release_ratio` represents the proportion of the publisher's portfolio classified as recent.

The ratio was calculated as:

`recent_release_ratio = recent_release_count / game_count`

The two measures distinguish between the absolute amount of recent publishing activity and the proportion of the publisher's portfolio that is recent.

### Minimum Portfolio Size

Only publishers associated with at least **10 games** were retained for subsequent normalization and scoring.

A minimum portfolio size was imposed because publisher-level averages based on only a small number of games may be highly sensitive to individual titles and therefore provide a less reliable representation of sustained publisher performance.

A threshold of 10 games was selected as a practical minimum for representing an established portfolio while also retaining a sufficiently broad publisher population for comparison.

The threshold additionally reduced the analysis to fewer than 1,000 eligible publishers.

---

## Feature Normalization

Publisher-level features were measured on different scales and followed different distributions. Normalization was therefore applied before the features were combined into dimension scores.

Original feature values were retained, and normalized values were written to separate `_norm` variables.

The normalization method was selected according to the observed publisher-level distribution of each feature rather than applying the same transformation to every variable.

### Distribution-Based Normalization

For the following features, skewness was calculated after publisher-level aggregation:

* `avg_owners_mid`
* `avg_language_count`
* `game_count`
* `recent_release_count`

An absolute skewness threshold of **2** was used as an operational indicator of substantial distributional asymmetry.

Where:

`|skewness| > 2`

the feature was first transformed using `log1p` to reduce the influence of a heavy right tail and was subsequently min-max scaled to the 0–1 range.

Features not exceeding the threshold were min-max scaled without the logarithmic transformation.

### Active-User Rate

`avg_active_users_rate` required different treatment.

Extreme values made conventional min-max scaling highly sensitive to outliers, which would compress most publishers into a narrow portion of the resulting scale.

The variable was therefore transformed using a **percentile rank**.

Consequently, `avg_active_users_rate_norm` represents a publisher's relative position among the eligible publishers rather than a literal percentage of owners who remain active.

For example, a value near `0.90` indicates a position around the 90th percentile of the publisher distribution.

### Bounded Variables

The following variables were not normalized during publisher-level feature construction because they were already bounded and directly interpretable:

* `review_score`
* `avg_positive_review_ratio`
* `recent_release_ratio`

The publisher-level `review_score` was subsequently min-max normalized only when constructing the Quality dimension so that it could be combined with the 0–1 positive-review ratio.

---

## Publisher-Level Performance Dimensions

The normalized and bounded publisher-level features were combined into four performance dimensions.

### Scale & Reach

**Purpose:** Represent the typical audience reach and accessibility of a publisher's games.

| Component                 | Weight |
| ------------------------- | -----: |
| `avg_owners_mid_norm`     |    80% |
| `avg_language_count_norm` |    20% |

`avg_owners_mid_norm` represents normalized average estimated ownership per game, while `avg_language_count_norm` represents normalized average language availability.

Estimated ownership received greater weight because it provides a more direct indication of demonstrated audience reach. Language availability was treated as a complementary measure of a game's accessibility across markets.

**Calculation**

`Scale & Reach = 0.80 × avg_owners_mid_norm + 0.20 × avg_language_count_norm`

### Quality

**Purpose:** Represent player reception of a publisher's games.

| Component                   | Weight |
| --------------------------- | -----: |
| `review_score_norm`         |    50% |
| `avg_positive_review_ratio` |    50% |

`review_score_norm` is the normalized version of the publisher-level mean review score. `avg_positive_review_ratio` represents the mean game-level proportion of positive reviews.

The publisher-level review score was retained in its original interpretable form in `publisher_features.csv` and was min-max normalized to the 0–1 range only when constructing the Quality dimension.

The two measures capture related but distinct aspects of player reception. The review score summarizes Steam's review-performance classification, while the positive-review ratio provides a continuous measure of the proportion of favorable reviews.

Neither measure was considered sufficiently informative to dominate the dimension, and they were therefore assigned equal weights.

**Calculation**

`Quality = 0.50 × review_score_norm + 0.50 × avg_positive_review_ratio`

### Engagement

**Purpose:** Represent continued player activity relative to accumulated ownership.

Engagement was represented by `avg_active_users_rate_norm`, the percentile-ranked version of the publisher's average active-user rate.

The underlying active-user rate relates concurrent users to estimated ownership and therefore complements Scale & Reach by distinguishing accumulated audience size from continued player activity.

This supports the objective of identifying publishers whose games continue to attract players rather than publishers whose performance is driven exclusively by historical ownership.

Because Engagement was represented by a single feature, no additional within-dimension weighting was required.

**Calculation**

`Engagement = avg_active_users_rate_norm`

### Growth & Momentum

**Purpose:** Capture recent publishing activity rather than total historical portfolio size.

| Component                   | Weight |
| --------------------------- | -----: |
| `recent_release_ratio`      |    60% |
| `recent_release_count_norm` |    40% |

`recent_release_ratio` represents the proportion of the publisher's portfolio released within the defined two-year period.

`recent_release_count_norm` represents the normalized absolute number of recent releases.

The recent-release ratio received slightly greater weight because it indicates how strongly a publisher's current portfolio is oriented toward recent activity regardless of total portfolio size.

The absolute recent-release count complements this measure by distinguishing publishers that have released a larger number of games within the same period.

**Calculation**

`Growth & Momentum = 0.60 × recent_release_ratio + 0.40 × recent_release_count_norm`

Using recent-release measures rather than total portfolio size was intended to make the dimension reflect current publishing momentum rather than rewarding publishers primarily for having accumulated a large historical catalogue.

---

## Overall Publisher Score

The four dimension scores were combined into a single overall publisher score using a **weighted additive scoring model**.

### Baseline Weights

| Dimension         |   Weight |
| ----------------- | -------: |
| Scale & Reach     |      35% |
| Quality           |      30% |
| Engagement        |      20% |
| Growth & Momentum |      15% |
| **Total**         | **100%** |

**Calculation**

`Overall Score = 0.35 × Scale & Reach + 0.30 × Quality + 0.20 × Engagement + 0.15 × Growth & Momentum`

### Weighting Rationale

The four dimensions were assigned different weights according to their relative importance for identifying consistently high-performing publishers.

**Scale & Reach — 35%**

Scale & Reach received the highest weight because the ability to attract a comparatively large audience provides an indication of market presence and commercial scale.

Within the scoring framework, this dimension reflects the typical reach and accessibility of games within a publisher's portfolio.

**Quality — 30%**

Quality received the second-highest weight because audience reach alone does not necessarily indicate sustainable performance.

Positive player reception provides evidence that a publisher's games meet player expectations and can contribute to customer satisfaction, reputation, and longer-term trust in the publisher.

**Engagement — 20%**

Engagement captures continued player activity relative to accumulated ownership.

This dimension complements Scale & Reach by distinguishing games that have reached a large audience from games that continue to attract active players. It therefore supports the objective of identifying publishers with sustained performance rather than those whose success is driven primarily by isolated releases.

**Growth & Momentum — 15%**

Growth & Momentum incorporates recent publishing activity into the assessment.

Although established and consistent performance was prioritized, recent activity provides additional information about whether a publisher continues to develop its portfolio.

The lower weight prevents recent publishing activity from outweighing demonstrated performance across the other dimensions while still rewarding publishers showing continued momentum.

### Interpretation of the Weights

The resulting **35% / 30% / 20% / 15%** weighting represents an analytical judgment about the relative importance of the four dimensions rather than an objectively determined weighting scheme.

A sensitivity analysis was therefore conducted to assess how strongly the overall scores of the highest-ranked publishers depended on plausible alternative top-level weighting assumptions.

### Missing Dimension Scores

Missing dimension scores were not compensated for by redistributing their weights across the remaining dimensions.

If any of the four required dimension scores was missing, the publisher's overall score was also treated as missing.

This ensured that all ranked publishers were evaluated using the same effective scoring structure.

---

## Publisher Ranking

Publishers with complete overall scores were ranked in descending order.

Higher overall scores indicate stronger performance according to the scoring framework.

### Ties

Tied overall scores were assigned the same rank using a minimum-rank approach.

Publishers with identical overall scores therefore received the same highest applicable ranking position.

### Score Validation

The calculated dimension scores and overall scores were checked to ensure that all non-missing values remained within the expected **0–1 range**.

---

## Sensitivity Analysis

Because the overall publisher score depends partly on the weights assigned to the four performance dimensions, a sensitivity analysis was conducted to assess how strongly publisher scores depend on the baseline weighting assumptions.

The purpose of the sensitivity analysis was not to identify or optimize an alternative weighting scheme. Instead, it served as a robustness check by examining how much the scores of the highest-ranked publishers could change under reasonable alternative top-level weights.

The internal dimension scores were held constant throughout the analysis. Only the four top-level weights assigned to Scale & Reach, Quality, Engagement, and Growth & Momentum were varied. This ensured that the sensitivity analysis isolated the effect of the top-level weighting assumptions without changing the underlying feature construction or dimension definitions.

### Weight Scenarios

The baseline weights were varied within the following ranges:

| Dimension         | Baseline | Tested range |
| ----------------- | -------: | -----------: |
| Scale & Reach     |      35% |       25–45% |
| Quality           |      30% |       20–40% |
| Engagement        |      20% |       10–30% |
| Growth & Momentum |      15% |        5–25% |

Each dimension was allowed to vary by up to **10 percentage points above or below its baseline weight**. The tested values were defined in increments of **5 percentage points**.

All possible combinations of the specified values were generated programmatically. Only combinations in which the four weights summed to exactly 100% were retained as valid scenarios. The baseline weighting of 35% / 30% / 20% / 15% was included among the valid combinations.

For each valid combination, a new overall publisher score was calculated using the existing four dimension scores:

`Scenario Score = w₁ × Scale & Reach + w₂ × Quality + w₃ × Engagement + w₄ × Growth & Momentum`

The underlying dimension scores remained unchanged across all scenarios.

### Baseline Top-10 Score Sensitivity

The ten highest-ranked publishers were identified using their original baseline `overall_score` before the sensitivity results were examined. This ensured that publishers were selected according to the original scoring model rather than according to their performance under alternative weighting scenarios.

For each of these baseline Top 10 publishers, three values were calculated:

| Measure        | Description                                                               |
| -------------- | ------------------------------------------------------------------------- |
| Minimum score  | Lowest overall score across all valid weighting combinations              |
| Baseline score | Original overall score under the 35% / 30% / 20% / 15% baseline weighting |
| Maximum score  | Highest overall score across all valid weighting combinations             |

The resulting score ranges were used to evaluate how strongly each leading publisher's numerical score depended on the selected top-level weights.

The analysis evaluates **score sensitivity rather than ranking sensitivity**. It therefore does not assess rank changes, rank correlations, or Top-N retention under alternative weighting scenarios.

---

## Validation

Validation checks were incorporated throughout publisher-feature construction, scoring, and sensitivity analysis.

### Publisher-Feature Validation

The publisher-level dataset was checked to confirm that:

* each publisher occurred only once;
* all retained publishers met the minimum portfolio-size requirement;
* normalized variables fell within their expected ranges;
* numerical variables did not contain infinite values; and
* missingness was assessed after aggregation and normalization.

### Scoring Validation

During scoring:

* the four dimension scores were checked to ensure that all non-missing values fell within the expected 0–1 range;
* the overall score was checked against the same range;
* publisher identifiers were checked for duplicates; and
* publishers with missing overall scores were identified rather than silently removed or reweighted.

### Sensitivity-Analysis Validation

The sensitivity analysis was checked to ensure that:

* each set of top-level weights remained within its predefined range;
* each weight used one of the specified 5-percentage-point increments;
* the four weights summed to exactly 100%;
* each valid weighting combination occurred only once; and
* the baseline 35% / 30% / 20% / 15% weighting was included among the valid scenarios.

The four underlying dimension scores were held constant across scenarios so that only the effect of changing the top-level weights was assessed.

For each valid weighting combination, the recalculated overall scores were checked to ensure that non-missing values remained within the expected 0–1 range.

The baseline Top 10 publishers were selected using the original `overall_score` before the alternative scenario results were examined. Their minimum and maximum scenario scores were then calculated across the complete set of valid weighting combinations.

These validation procedures were intended to ensure that differences in the observed score ranges resulted from changes in the top-level weighting assumptions rather than changes in publisher selection, feature construction, dimension construction, or scenario generation.

