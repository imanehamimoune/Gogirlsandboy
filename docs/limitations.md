# Limitations

## Scope of the Analysis

The scoring framework provides a quantitative comparison of publishers based primarily on game-level performance data available in the underlying Steam and SteamSpy datasets. The resulting scores should therefore be interpreted as a **screening and prioritization tool rather than a complete assessment of publisher value or investment suitability**.

The analysis does not directly measure several factors that would be important for an acquisition, investment, or strategic partnership decision, including company valuation, profitability, debt, intellectual-property ownership, management quality, transaction willingness, organizational compatibility, and expected acquisition synergies. These factors require separate strategic and financial due diligence.


## PC and Steam Market Bias

The underlying data primarily reflect performance within the PC and Steam ecosystem. Publisher performance on consoles, mobile platforms, proprietary storefronts, subscription services, and other distribution channels is not comprehensively represented.

This is particularly relevant to the Microsoft decision context because strong Steam performance does not necessarily imply equivalent performance within the Xbox ecosystem. Conversely, publishers with strong console or mobile businesses may be undervalued by the scoring framework if those activities are not adequately represented in the available data.

The publisher scores should therefore be interpreted as indicators of performance within the observed market rather than measures of total cross-platform publisher performance.


## SteamSpy Ownership Estimates

Audience reach is partly measured using SteamSpy ownership estimates. SteamSpy reports ownership as ranges rather than exact ownership counts. The analysis uses the midpoint of each range as a single-value approximation.

Consequently, `owners_mid` does not represent an exact number of customers. Publishers whose games fall within wide ownership ranges may have substantial uncertainty around their estimated reach.

Furthermore, ownership represents estimated game acquisition rather than confirmed unit sales or unique publisher-level customers. The Scale & Reach dimension should therefore be interpreted as a proxy for typical audience reach rather than an exact measure of publisher sales.


## Revenue Estimation

An estimated-revenue variable was constructed as:

`estimated revenue = ownership midpoint × current price`

However, this measure was not included as a performance dimension because it was considered insufficiently reliable for publisher valuation.

The estimate does not account for historical selling prices, discounts at the time of purchase, regional pricing, bundles, refunds, free copies, free-to-play monetization, taxes, platform fees, or Steam's revenue share. SteamSpy ownership itself is also estimated as a range.

The resulting variable therefore represents a rough analytical proxy rather than actual realized revenue and should not be used as a substitute for publisher financial statements or transaction valuation.


## Publisher Coverage

The master dataset contained a substantial number of games for which `publisher_primary` was unavailable. A total of **49,738 game records, representing 35.5% of the master dataset**, could not be assigned to a publisher and were therefore excluded from publisher-level aggregation.

The publisher-level results consequently describe only games for which a publisher could be identified. If missing publisher information is systematically associated with particular types of games or publishers, the resulting publisher population may not be fully representative.


## Minimum Portfolio-Size Requirement

Only established publishers represented by **at least 10 games** in the dataset were retained for scoring. This reduced the publisher population from **46,239 publishers** identified during aggregation to **814 eligible publishers**.

The threshold improves the stability of publisher-level averages by reducing the influence of publishers represented by only a small number of titles. However, it also excludes smaller and emerging publishers that may represent attractive investment opportunities.

The resulting ranking should therefore be interpreted as an evaluation of comparatively established publishers rather than the complete publisher market.

The threshold of 10 games is also an analytical judgment rather than a statistically optimized cutoff. Different minimum portfolio requirements could produce a different eligible publisher population.


## Missing Review Information

Complete overall scores were available for **790 of the 814 eligible publishers**. The remaining 24 publishers could not receive an overall score because information required for the Quality dimension was unavailable.

The scoring model deliberately does not impute missing dimension scores or redistribute their weights. This preserves a consistent scoring structure across ranked publishers but means that publishers with insufficient review information cannot be ranked even if sufficient information is available for the other dimensions.

In addition, a Steam `review_score` of zero was interpreted as insufficient information to calculate a review score rather than poor game quality and was excluded from publisher-level averaging. This treatment follows the meaning assigned to the variable in the dataset but reduces the number of observations contributing to some publisher Quality measures.


## Equal Weighting of Games Within Publishers

Several publisher-level features are calculated as averages across games. This means that individual games generally receive equal influence regardless of their commercial scale.

For example, the publisher-level positive-review ratio is the mean of individual game-level positive-review ratios rather than the ratio of all positive reviews to all reviews across the publisher's portfolio. Similarly, average ownership measures the typical estimated ownership of a publisher's games rather than total publisher ownership.

This approach prevents a single blockbuster title from completely dominating a publisher's score, but it may understate the importance of commercially significant flagship games.


## Active-User Rate

Engagement is based on the relationship between `concurrent_users_yesterday` and estimated ownership. This measure represents a snapshot of player activity rather than long-term retention.

Concurrent-user levels may vary because of release timing, updates, promotions, seasonality, weekends, live events, or other temporary factors. A publisher's Engagement score may therefore depend partly on when the underlying data were collected.

Furthermore, the ownership denominator is itself based on SteamSpy estimates.

Because extreme active-user-rate observations made conventional scaling unsuitable, publisher-level Engagement was normalized using a percentile rank. The resulting Engagement score therefore represents a publisher's **relative position among eligible publishers**, not the literal percentage of owners who are currently active.


## Recent-Release Definition

Growth & Momentum is based on games released within **two years of the latest release date observed in the dataset**. Using the dataset's maximum release date as a fixed reference point makes the analysis reproducible for a static data snapshot, but the two-year window remains an analytical choice.

A different definition of recent activity could change publisher Growth & Momentum scores.

The measure also relies on listed release dates. It does not fully capture ongoing development activity such as major updates, downloadable content, expansions, live-service development, or continued investment in older games.

This is particularly relevant when interpreting publishers such as Valve. Valve receives a Growth & Momentum score of zero under the defined metric because none of its observed games with usable release dates qualify as recent releases. This does not necessarily imply that Valve as a company has no growth or current development activity; it means only that no qualifying recent releases were captured by this specific measure.


### Live-Service and Relaunched Games

The release-date-based definition of Growth & Momentum may underestimate the current activity of publishers operating long-running or continuously updated games. The metric captures whether games were released within two years of the dataset's reference date, but it does not capture continued development through major updates, expansions, live-service content, or relaunches.

Valve provides a relevant example. Its most recent game with a valid release date in the dataset is *Half-Life: Alyx*, released in March 2020, which falls outside the two-year window relative to the dataset's October 2024 reference date. Valve therefore has a calculated `recent_release_count` of zero.

However, actively maintained titles such as *Counter-Strike 2* and *Dota 2* have missing `release_date` values in the analyzed data. Because observations without a valid release date cannot satisfy the recent-release condition, these titles do not contribute to Valve's Growth & Momentum score. The resulting score of `0.000` is therefore consistent with the implemented calculation but may understate Valve's actual recent development activity.

More generally, this represents a limitation for publishers whose strategy emphasizes long-running live-service games, major updates, or relaunches rather than frequent new releases. Growth & Momentum should therefore be interpreted specifically as **recent release activity captured by the available release-date data**, rather than as a comprehensive measure of company growth, development activity, or product investment.


## Normalization

Several variables required normalization before they could be combined into dimension scores.

Highly skewed variables were transformed using `log1p` followed by min-max scaling, while Engagement was represented using percentile ranks. These transformations improve comparability between variables but also change their interpretation.

Min-max normalization is dependent on the observed publisher population and its extreme values. Scores could therefore change if the underlying dataset or eligible publisher population changes.

Similarly, percentile normalization measures relative position rather than absolute performance. A publisher's normalized Engagement score may therefore change even if its underlying engagement remains unchanged but the comparison population changes.


## Subjective Weighting Assumptions

The overall score depends on analyst-defined weights:

| Dimension | Weight |
| --- | ---: |
| Scale & Reach | 35% |
| Quality | 30% |
| Engagement | 20% |
| Growth & Momentum | 15% |
| **Total** | **100%** |

Additional assumptions are made within the dimensions, including the **80/20** weighting of ownership and language availability, the **50/50** Quality weighting, and the **60/40** Growth & Momentum weighting.

These weights reflect the project's interpretation of the relative importance of the performance indicators and are **not objectively determined values**.

A sensitivity analysis was therefore conducted to examine how the numerical scores of the baseline Top 10 change when the four top-level weights vary by ±10 percentage points. The analysis found meaningful score variation, demonstrating that publisher scores depend partly on the chosen weighting assumptions.

However, the sensitivity analysis varies only the top-level dimension weights. It does not test alternative internal dimension weights, feature definitions, normalization methods, minimum portfolio thresholds, or recent-release windows.


## Sensitivity Analysis Does Not Test Ranking Stability

The sensitivity analysis evaluates the range of numerical scores produced under alternative top-level weighting assumptions.

It does not evaluate whether publishers change ranking positions under those scenarios. In particular, the analysis does not calculate rank changes, rank correlations, Top-N retention, or shortlist membership across alternative weight combinations.

Overlapping score ranges between publishers therefore cannot be interpreted as evidence that one publisher overtakes another under a particular scenario. The minimum and maximum scores of different publishers may occur under different weight combinations.

The sensitivity analysis should consequently be interpreted as a test of **score sensitivity rather than ranking robustness**.


## Strategic and Transaction Feasibility

The quantitative scoring model evaluates publisher performance but does not directly model whether a transaction is feasible.

This distinction is visible in the final shortlist. PlayStation Publishing LLC achieves a high quantitative ranking but is excluded from the actionable candidate set because it belongs to a direct platform competitor. Xbox Game Studios is similarly excluded because it is already part of Microsoft.

The remaining candidates also require different strategic approaches. Valve's private ownership and position as a major industry player make a conventional acquisition difficult, while CAPCOM's scale makes a full acquisition substantially more capital-intensive. Coffee Stain Publishing represents a comparatively more actionable acquisition candidate within the assumptions of the project.

These considerations were assessed after the quantitative ranking and are not represented in the publisher scores themselves. A high score therefore indicates **quantitative attractiveness, not transaction feasibility**.


## Business and Financial Factors Outside the Model

The scoring framework does not incorporate several variables that would be necessary for a complete investment decision, including:

- market capitalization or private-company valuation;
- acquisition premium;
- profitability and cash flow;
- debt and other liabilities;
- intellectual-property value;
- expected synergies;
- development pipeline;
- employee and management retention;
- regulatory risk;
- willingness of owners to sell;
- integration costs;
- platform and subscription-service fit; and
- expected return on invested capital.

These factors may materially change the relative attractiveness of publishers after the quantitative screening stage.

For this reason, the shortlist should be followed by publisher-specific strategic and financial due diligence rather than interpreted as a direct recommendation to acquire the highest-scoring publisher.


## Overall Interpretation

The analysis provides a reproducible framework for comparing established publishers using available game-performance indicators. Its main strength is the combination of several dimensions rather than reliance on a single KPI.

However, the resulting scores remain dependent on the available Steam-focused data, proxy measures, normalization choices, eligibility criteria, feature definitions, and analyst-defined weights. The model also measures historical and observed game performance rather than company valuation or transaction feasibility.

The results should therefore be interpreted as a **quantitative screening tool for identifying publishers that warrant deeper investigation**, not as a comprehensive valuation model or a definitive acquisition recommendation.

Further strategic, financial, legal, and market-specific due diligence is required before translating the quantitative shortlist into an investment, acquisition, or partnership decision.
