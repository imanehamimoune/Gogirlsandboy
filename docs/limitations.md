# Limitations

## Scope of the Analysis

The scoring framework provides a quantitative comparison of publishers based primarily on game-level performance data from the underlying Steam and SteamSpy datasets.

The resulting scores should be interpreted as a **screening and prioritization tool rather than a complete assessment of publisher value or investment suitability**.

The analysis does not directly measure several factors required for an acquisition, investment, or strategic partnership decision, including:

* company valuation;
* profitability and cash flow;
* debt and other liabilities;
* intellectual-property ownership and value;
* management quality;
* transaction willingness;
* organizational compatibility; and
* expected acquisition synergies.

These factors require separate strategic and financial due diligence.

---

## Market Coverage

### PC and Steam Market Bias

The underlying data primarily reflect performance within the **PC and Steam ecosystem**.

Publisher performance on the following channels is not comprehensively represented:

* consoles;
* mobile platforms;
* proprietary storefronts;
* subscription services; and
* other distribution channels.

This is particularly relevant to the Microsoft decision context. Strong Steam performance does not necessarily imply equivalent performance within the Xbox ecosystem. Conversely, publishers with strong console or mobile businesses may be undervalued if those activities are not adequately represented in the available data.

Publisher scores should therefore be interpreted as indicators of performance **within the observed market rather than measures of total cross-platform publisher performance**.

### Publisher Coverage

The master dataset contains **49,738 game records, representing 35.5% of the master dataset**, for which `publisher_primary` is unavailable.

These records could not be assigned to a publisher and were therefore excluded before publisher-level features were calculated.

As a result:

* publisher-level results describe only games for which a publisher could be identified;
* publishers disproportionately affected by missing publisher information may be incompletely represented; and
* some publishers may be absent from the scoring process entirely.

If missing publisher information is associated with particular types of games or publishers, the resulting publisher population may not be representative.

---

## SteamSpy Ownership Estimates

Audience reach is partly measured using SteamSpy ownership estimates.

SteamSpy reports ownership as **ranges rather than exact ownership counts**. The analysis uses the midpoint of each range as a single-value approximation.

Consequently, `owners_mid` does not represent an exact number of customers. Games falling within wide ownership ranges may have substantial uncertainty around their estimated reach.

Ownership also represents estimated game acquisition rather than:

* confirmed unit sales; or
* unique publisher-level customers.

The Scale & Reach dimension should therefore be interpreted as a **proxy for typical audience reach rather than an exact measure of publisher sales**.

---

## Revenue Estimation

An estimated-revenue variable was constructed as:

`estimated revenue = ownership midpoint × current price`

This measure was not included as a performance dimension because it was considered unreliable for publisher valuation.

The estimate does not account for:

* historical selling prices;
* discounts at the time of purchase;
* regional pricing;
* bundles;
* refunds;
* free copies;
* free-to-play monetization;
* taxes;
* platform fees; or
* Steam's revenue share.

In addition, the underlying SteamSpy ownership measure is itself estimated as a range.

The resulting variable represents a **rough analytical proxy rather than actual realized revenue**. It should not be used as a substitute for publisher financial statements or transaction valuation.

---

## Publisher Eligibility

### Minimum Portfolio Size

Only **established publishers represented by at least 10 games in the dataset** were retained for scoring.

This reduced the publisher population from **46,239 publishers** identified during aggregation to **814 eligible publishers**.

The threshold improves the stability of publisher-level averages by reducing the influence of publishers represented by only a small number of titles.

However, it also excludes smaller and emerging publishers that may represent attractive investment opportunities.

The resulting ranking should therefore be interpreted as an evaluation of **comparatively established publishers rather than the complete publisher market**.

The 10-game threshold is an analytical judgment rather than a statistically optimized cutoff. Different minimum portfolio requirements could change the eligible publisher population and potentially affect the resulting scores and rankings.

### Inclusion of Demo Titles

Demo titles were retained because they represent valid Steam applications and were not considered erroneous observations solely because of their product type.

However, demos may differ from full commercial releases. They are commonly free and may exhibit different:

* ownership patterns;
* review patterns; and
* engagement patterns.

Their inclusion may therefore influence publisher-level averages and, consequently, the Scale & Reach, Quality, and Engagement dimensions.

The analysis does not separately weight or exclude demo titles when constructing publisher-level features. Publishers with comparatively large numbers of demos may therefore be affected differently from publishers whose observed portfolios consist primarily of full releases.

---

## Portfolio-Level Aggregation

Several publisher-level features are calculated as averages across games. Individual games therefore generally receive **equal influence regardless of their commercial scale**.

For example:

* `avg_positive_review_ratio` is calculated as the mean of individual game-level positive-review ratios rather than the ratio of all positive reviews to all reviews across the publisher's portfolio.
* Average ownership represents the typical estimated ownership of a publisher's games rather than total publisher ownership.

This approach prevents a single blockbuster title from completely dominating a publisher's score.

However, it may also understate the importance of commercially significant flagship games.

Publisher scores should therefore primarily be interpreted as measures of the **typical performance of games within a publisher's portfolio**, rather than measures of total portfolio scale or total commercial performance.

---

## Quality Dimension

The Quality dimension depends partly on the availability of meaningful review information.

Although only a small number of records have a formally missing `review_score`, **78,137 games in the master dataset have `review_score == 0`**.

A score of zero represents insufficient review information rather than poor game quality and was therefore excluded from publisher-level review-score averaging.

As a result, the publisher-level `review_score` may be calculated from only a subset of a publisher's portfolio. Publishers with many games that have insufficient review activity may therefore have their review-score component determined by a comparatively small number of titles.

### Missing Quality Scores

Complete overall scores were available for **790 of the 814 eligible publishers**.

The remaining **24 publishers** could not receive an overall score because information required for the Quality dimension was unavailable.

The scoring model deliberately does not:

* impute missing dimension scores; or
* redistribute missing weights across the remaining dimensions.

This preserves a consistent scoring structure across ranked publishers but means that publishers with insufficient Quality information cannot be ranked even when information for the other dimensions is available.

---

## Engagement Dimension

Engagement is based on the relationship between `concurrent_users_yesterday` and estimated ownership.

### Snapshot Measurement

`concurrent_users_yesterday` represents a snapshot of player activity rather than long-term retention.

Concurrent-user levels may vary because of:

* release timing;
* updates;
* promotions;
* seasonality;
* weekends;
* live events; or
* other temporary factors.

A publisher's Engagement score may therefore depend partly on when the underlying data were collected.

The ownership denominator is also based on SteamSpy estimates, introducing additional uncertainty.

### Relative Normalization

Extreme active-user-rate observations made conventional scaling unsuitable. Publisher-level Engagement was therefore normalized using a **percentile rank**.

The resulting Engagement score represents a publisher's **relative position among eligible publishers**, not the literal percentage of owners who are currently active.

A publisher's normalized Engagement score may consequently change if the comparison population changes, even when its underlying active-user rate remains unchanged.

---

## Growth & Momentum Dimension

Growth & Momentum should be interpreted specifically as **recent release activity captured by the available release-date data**, rather than as a comprehensive measure of company growth, development activity, or product investment.

Two limitations are particularly important: release-date coverage and the definition of a recent release.

### Release-Date Coverage

The master dataset contains **28,520 games with missing `release_date` values, corresponding to approximately 20.4% of all games**.

Games without a valid release date cannot be classified as recent under the implemented methodology and therefore cannot contribute to `recent_release_count`.

If release-date missingness is not randomly distributed across publishers or types of games, Growth & Momentum may systematically underestimate recent publishing activity for some publishers.

This limitation affects both:

* `recent_release_count`; and
* `recent_release_ratio`.

### Recent-Release Definition

A game is classified as recent if it was released within **two years of the latest release date observed in the dataset**.

Using the dataset's maximum release date as a fixed reference point makes the analysis reproducible for a static data snapshot.

However, the two-year window remains an analytical choice rather than an objectively determined definition of publishing momentum. A shorter or longer window could produce different recent-release counts, ratios, and Growth & Momentum scores.

The measure also relies on listed release dates and therefore does not fully capture other forms of current publisher activity, including:

* major updates;
* downloadable content;
* expansions;
* live-service development; and
* continued investment in older titles.

### Live-Service and Relaunched Games

The release-date-based definition may particularly underestimate publishers operating long-running or continuously updated games.

Valve provides a relevant example.

Its most recent title with a valid release date in the dataset is *Half-Life: Alyx*, released in March 2020. This falls outside the two-year recent-release window relative to the dataset's October 2024 reference date.

Valve therefore has:

* `recent_release_count = 0`; and
* Growth & Momentum = `0.000`.

However, actively maintained titles such as *Counter-Strike 2* and *Dota 2* have missing `release_date` values in the analyzed master dataset. Because observations without a valid release date cannot satisfy the recent-release condition, these titles do not contribute to Valve's Growth & Momentum score.

The resulting score of `0.000` is therefore consistent with the implemented calculation but should **not** be interpreted as evidence that Valve has no ongoing development activity or business growth.

More generally, Growth & Momentum may undervalue publishers whose strategies emphasize long-running live-service games, major updates, expansions, or relaunches rather than frequent releases of new titles.

---

## Normalization

Several publisher-level variables required normalization before they could be combined into dimension scores.

The analysis uses two main approaches:

| Method                              | Application             | Interpretation Limitation                            |
| ----------------------------------- | ----------------------- | ---------------------------------------------------- |
| `log1p` followed by min-max scaling | Highly skewed variables | Depends on the observed range and extreme values     |
| Percentile rank                     | Engagement              | Represents relative rather than absolute performance |

These transformations improve comparability between variables measured on different scales but also change how normalized values should be interpreted.

### Min-Max Scaling

Min-max normalization depends on the observed publisher population and its extreme values.

Normalized scores could therefore change if:

* the underlying dataset changes;
* the eligible publisher population changes; or
* the observed minimum and maximum values change.

### Percentile Ranking

Percentile normalization measures relative position rather than absolute performance.

A publisher's normalized Engagement score may therefore change even when its underlying engagement remains unchanged if the comparison population changes.

Normalization consequently improves comparability **within the analyzed dataset**, but it does not create absolute performance measures that can necessarily be compared unchanged across different datasets or time periods.

---

## Weighting Assumptions

The overall publisher score depends on analyst-defined weights:

| Dimension         |   Weight |
| ----------------- | -------: |
| Scale & Reach     |      35% |
| Quality           |      30% |
| Engagement        |      20% |
| Growth & Momentum |      15% |
| **Total**         | **100%** |

Additional weighting assumptions are made within the individual dimensions:

| Dimension         | Internal Weighting                                  |
| ----------------- | --------------------------------------------------- |
| Scale & Reach     | 80% ownership / 20% language availability           |
| Quality           | 50% review score / 50% positive-review ratio        |
| Growth & Momentum | 60% recent-release ratio / 40% recent-release count |

These weights reflect the project's interpretation of the relative importance of the performance indicators and are **not objectively determined values**.

### Sensitivity Analysis

A sensitivity analysis examined how the numerical scores of the baseline Top 10 changed when the four top-level dimension weights varied by ±10 percentage points.

The results showed meaningful score variation, confirming that numerical publisher assessments depend partly on the selected weighting assumptions.

However, the sensitivity analysis varies only the **top-level dimension weights**.

It does not test alternative:

* internal dimension weights;
* feature definitions;
* normalization methods;
* minimum portfolio-size thresholds; or
* recent-release windows.

### Score Sensitivity vs. Ranking Stability

The sensitivity analysis evaluates **score sensitivity rather than ranking robustness**.

It does not calculate:

* rank changes;
* rank correlations;
* Top-N retention; or
* shortlist membership under alternative weight combinations.

Overlapping score ranges therefore cannot be interpreted as evidence that one publisher overtakes another under a particular scenario. The minimum and maximum scores of different publishers may occur under different weight combinations.

A separate ranking-sensitivity analysis would be required to determine whether the composition or ordering of the highest-ranked publishers remains stable under alternative weighting assumptions.

---

## Strategic and Transaction Feasibility

The quantitative scoring model evaluates publisher performance but does not directly determine whether an acquisition, investment, or partnership is feasible.

This distinction is visible in the final shortlist.

* **PlayStation Publishing LLC** achieves a high quantitative ranking but is excluded from the actionable candidate set because it belongs to a direct platform competitor.
* **Xbox Game Studios** is excluded because it is already part of Microsoft.

The remaining candidates also require different strategic approaches:

| Candidate               | Feasibility Consideration                                                               |
| ----------------------- | --------------------------------------------------------------------------------------- |
| Valve                   | Private ownership and major industry position make a conventional acquisition difficult |
| Coffee Stain Publishing | Comparatively more actionable acquisition candidate within the project's assumptions    |
| CAPCOM Co., Ltd.        | Scale makes a full acquisition substantially more capital-intensive                     |

These considerations were assessed **after** the quantitative ranking and are not represented in the publisher scores themselves.

A high publisher score should therefore be interpreted as an indication of **quantitative attractiveness rather than transaction feasibility**.

---

## Business and Financial Factors Outside the Model

The scoring framework does not incorporate several factors required for a complete investment decision:

* market capitalization or private-company valuation;
* acquisition premium;
* profitability and cash flow;
* debt and other liabilities;
* intellectual-property value;
* expected synergies;
* development pipeline;
* employee and management retention;
* regulatory risk;
* willingness of owners to sell;
* integration costs;
* platform and subscription-service fit; and
* expected return on invested capital.

These factors may materially change the relative attractiveness of publishers after the quantitative screening stage.

The model also does not determine whether an:

* acquisition;
* minority investment;
* distribution agreement; or
* strategic partnership

would create greater value for Microsoft.

The appropriate transaction structure requires candidate-specific assessment.

The shortlist should therefore be followed by publisher-specific strategic and financial due diligence rather than interpreted as a direct recommendation to acquire the highest-scoring publisher.

---

## Overall Interpretation

The analysis provides a reproducible framework for comparing established publishers using available game-performance indicators. Its main strength is the combination of several performance dimensions rather than reliance on a single KPI.

The results are nevertheless subject to several important limitations:

| Area                 | Main Limitation                                                                        |
| -------------------- | -------------------------------------------------------------------------------------- |
| Market coverage      | Data primarily represent the PC and Steam ecosystem                                    |
| Publisher coverage   | 35.5% of game records lack `publisher_primary`                                         |
| Ownership            | SteamSpy provides estimated ownership ranges                                           |
| Revenue              | Revenue is an analytical proxy rather than observed financial performance              |
| Eligibility          | Publishers with fewer than 10 observed games are excluded                              |
| Product types        | Demo titles are retained alongside full releases                                       |
| Aggregation          | Publisher features generally represent typical rather than total portfolio performance |
| Quality              | Many games lack sufficient review information                                          |
| Engagement           | Based on a point-in-time activity measure and relative normalization                   |
| Growth & Momentum    | Depends on release-date coverage and a two-year recent-release definition              |
| Normalization        | Scores depend on the observed comparison population                                    |
| Weighting            | Dimension and feature weights reflect analytical judgment                              |
| Sensitivity          | Tests score variation, not ranking stability                                           |
| Feasibility          | Transaction and strategic considerations are outside the quantitative score            |
| Financial assessment | Valuation, profitability, synergies, and expected returns are not modeled              |

The analysis therefore primarily measures **observed game and portfolio performance**. It does not directly measure company value, financial health, strategic fit, or transaction feasibility.

The results should be interpreted as a **quantitative screening tool for identifying established publishers that warrant deeper investigation**, not as a comprehensive valuation model or definitive acquisition recommendation.

Further strategic, financial, legal, competitive, and market-specific due diligence is required before translating the quantitative shortlist into an investment, acquisition, or partnership decision.
