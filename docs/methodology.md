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

A sensitivity analysis was therefore conducted to assess whether the resulting rankings remained stable under plausible alternative top-level weighting assumptions.

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

Because the overall publisher ranking depends partly on the weights assigned to the four performance dimensions, a sensitivity analysis was conducted to assess how strongly the results depended on the baseline weighting assumptions.

The purpose of the sensitivity analysis was to assess the **robustness of the chosen baseline**, not to identify or optimize a different weighting scheme.

### What Was Varied

Only the four **top-level dimension weights** were varied.

The internal composition of the four dimensions remained constant throughout the analysis:

* Scale & Reach remained weighted 80/20 internally.
* Quality remained weighted 50/50 internally.
* Engagement retained its single-feature definition.
* Growth & Momentum remained weighted 60/40 internally.

This isolated the effect of changing the relative importance assigned to the four dimensions while keeping the underlying features and dimension definitions unchanged.

### Weight Scenarios

| Dimension         | Baseline | Tested range |
| ----------------- | -------: | -----------: |
| Scale & Reach     |      35% |       25–45% |
| Quality           |      30% |       20–40% |
| Engagement        |      20% |       10–30% |
| Growth & Momentum |      15% |        5–25% |

Each dimension was allowed to vary by up to **10 percentage points above or below its baseline weight**.

This range was selected to represent meaningful alternative weighting assumptions without fundamentally redefining the scoring framework.

Weights were varied in increments of **5 percentage points**.

All combinations within the specified ranges were generated programmatically, and only combinations whose four weights summed to 100% were retained as valid scenarios.

For every valid scenario, publisher overall scores and rankings were recalculated.

The following remained unchanged:

* publisher population,
* underlying features,
* feature normalization,
* missing-value treatment, and
* within-dimension weights.

---

## Ranking Stability

Each alternative ranking was compared with the baseline ranking using several complementary measures.

| Measure                       | Purpose                                                                                           |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| **Mean absolute rank change** | Measures the average magnitude of publisher movements relative to baseline positions              |
| **Spearman rank correlation** | Measures similarity between each scenario's publisher ranking and the baseline ranking            |
| **Top-N overlap**             | Measures how many baseline Top 5, Top 10, and Top 20 publishers remain in the corresponding group |

### Mean Absolute Rank Change

Mean absolute rank change provides a direct indication of how much publisher positions typically change under an alternative weighting scenario.

### Spearman Rank Correlation

Spearman rank correlation measures the similarity between each scenario's publisher ranking and the baseline ranking.

Values closer to 1 indicate that the overall ordering of publishers remained similar despite changes in the top-level weights.

### Top-N Overlap

Top-N overlap was calculated for:

* Top 5,
* Top 10, and
* Top 20.

It represents the proportion of publishers from the corresponding baseline group that remained within that group under each alternative weighting scenario.

### Joint Interpretation

These measures were considered jointly because overall ranking stability does not necessarily imply stability among the highest-ranked publishers.

A scenario may produce a high Spearman correlation while still changing membership within the Top 5 or Top 10.

---

## Publisher-Level Sensitivity

Sensitivity was also assessed separately for each publisher across all valid weighting scenarios.

### Publisher-Level Measures

For each publisher, the analysis calculated:

* minimum overall score,
* maximum overall score,
* mean overall score,
* score standard deviation,
* score range,
* minimum rank,
* maximum rank,
* rank range, and
* mean absolute change from the baseline rank.

The proportion of valid scenarios in which each publisher appeared in the following groups was also calculated:

* Top 5,
* Top 10,
* Top 20.

These measures were used to identify publishers whose relative performance remained stable across alternative weighting assumptions and publishers whose position was more dependent on the selected weights.

### Interpretation

No fixed threshold was imposed to classify publishers as stable or sensitive.

Instead, stability was evaluated using the observed combination of:

* rank range,
* score range,
* mean absolute rank change, and
* Top-N frequency.

---

## Dimension-Level Sensitivity

The relationship between individual dimension weights and overall ranking stability was examined across the valid sensitivity scenarios.

For each dimension, Pearson correlations were calculated between its assigned top-level weight and:

* mean absolute publisher rank change; and
* the Spearman correlation between the scenario ranking and the baseline ranking.

### Interpretation

These correlations were interpreted as **descriptive measures of association within the constrained scenario space rather than causal effects**.

Because the four weights were required to sum to 100%, increasing the weight assigned to one dimension necessarily required changes to one or more of the remaining dimensions.

The resulting associations therefore indicate which weighting changes were most strongly associated with ranking sensitivity within the tested scenarios, not which dimension independently caused ranking changes.

---

## Representative Weighting Scenarios

In addition to the complete sensitivity grid, controlled representative scenarios were constructed to provide more interpretable comparisons with the baseline model.

### Scenario Construction

For each of the four dimensions:

1. Its baseline weight was increased by **10 percentage points**.
2. The weights assigned to the other three dimensions were reduced proportionally according to their baseline shares.
3. Their relative proportions were therefore maintained.
4. The total weight remained 100%.

Publisher scores and rankings were recalculated under each representative scenario.

The following were then compared with the baseline:

* ranking similarity,
* mean absolute rank change,
* Top-5 overlap,
* Top-10 overlap,
* Top-20 overlap, and
* changes among highly ranked publishers.

The complete sensitivity grid remained the **primary robustness analysis**.

The representative scenarios were included to make the effect of placing substantially greater emphasis on one dimension at a time easier to interpret.

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

### Baseline Reconstruction

Before alternative sensitivity scenarios were evaluated, the baseline scoring model was reconstructed directly from `publisher_features.csv`.

The reconstruction used the same:

* feature definitions,
* within-dimension weights,
* top-level weights,
* missing-value treatment, and
* ranking method

as the original scoring procedure.

The reconstructed publisher population, dimension scores, overall scores, and ranks were then compared with `publisher_scores.csv` as a reference validation step.

### Sensitivity-Scenario Validation

Sensitivity scenarios were checked to ensure that:

* each set of weights remained within its predefined range;
* each set of weights summed to 100%;
* each scenario occurred only once; and
* the baseline scenario was included exactly once.

Scenario-level scores were checked to remain within the 0–1 range where available.

Publisher–scenario combinations were checked for duplicates, and rankings were independently verified against the calculated overall scores.

These validation procedures were intended to ensure that differences observed in the sensitivity analysis resulted from changes in the top-level weighting assumptions rather than inconsistencies in feature construction, scoring, or scenario generation.
