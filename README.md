# Publisher Investment & Partnership Analysis

## Project Overview

This project develops a quantitative framework for identifying high-performing video game publishers as potential acquisition, investment, or strategic partnership candidates from Microsoft's perspective.

Game-level data from Steam and SteamSpy are cleaned, integrated, and aggregated to publisher level. Publishers are then evaluated across four dimensions:

- **Scale & Reach** — audience reach and language accessibility
- **Quality** — player review performance
- **Engagement** — continued player activity relative to estimated ownership
- **Growth & Momentum** — recent publishing activity

The four dimensions are combined into an overall publisher score that is used to rank eligible publishers and create a focused shortlist for further strategic and financial assessment.

The quantitative ranking is intended as a **screening and prioritization tool rather than a complete company valuation or investment recommendation**.


## Business Context

Microsoft operates in a highly competitive gaming market in which publishers, intellectual property, player communities, and distribution ecosystems represent important strategic assets.

Competitors such as Sony and Tencent have used acquisitions, minority investments, and strategic partnerships to strengthen their gaming portfolios. This project examines whether publisher-level game-performance data can be used to systematically identify external publishers that may warrant further consideration by Microsoft.

The analysis therefore addresses the following question:

> **Which established game publishers demonstrate strong and sustained performance across market reach, quality, player engagement, and recent publishing activity, and should therefore be prioritized for further strategic evaluation?**

The quantitative assessment is followed by a basic feasibility screen because a high-performing publisher is not necessarily a realistic acquisition or partnership candidate.


## Analytical Pipeline

The project follows five main stages:

1. **Data preparation**  
   Raw Steam and SteamSpy datasets are cleaned and standardized before being combined into a game-level master dataset.

2. **Publisher-level aggregation**  
   Game-level observations are aggregated to one row per publisher. Publishers represented by fewer than 10 games are excluded to focus the analysis on comparatively established publishers.

3. **Quantitative scoring**  
   Publisher-level features are combined into four performance dimensions and an overall weighted score.

4. **Candidate shortlist**  
   Publishers are ranked by overall score and combined with basic strategic-feasibility considerations to identify a focused shortlist.

5. **Sensitivity analysis**  
   Alternative top-level dimension weights are tested to assess how strongly the scores of the baseline Top 10 publishers depend on the selected weighting assumptions.


## Scoring Framework

The baseline scoring framework uses the following weights:

| Dimension | Weight | Components |
| --- | ---: | --- |
| Scale & Reach | 35% | 80% estimated ownership, 20% language availability |
| Quality | 30% | 50% review score, 50% positive-review ratio |
| Engagement | 20% | Active-user rate |
| Growth & Momentum | 15% | 60% recent-release ratio, 40% recent-release count |
| **Total** | **100%** | |

The weights represent analytical judgments about the relative importance of the four dimensions rather than objectively determined values. The sensitivity analysis therefore tests alternative top-level weighting assumptions.

Detailed feature definitions, normalization procedures, aggregation rules, and weighting rationale are documented in [`docs/methodology.md`](docs/methodology.md).


## Key Results

After publisher-level aggregation, **814 publishers** met the minimum requirement of at least 10 games. Complete overall scores were available for **790 publishers**.

Under the baseline scoring model, the highest-ranked publishers were:

| Rank | Publisher | Overall Score |
| ---: | --- | ---: |
| 1 | Valve | 0.783 |
| 2 | Coffee Stain Publishing | 0.767 |
| 3 | PlayStation Publishing LLC | 0.764 |
| 4 | CAPCOM Co., Ltd. | 0.740 |
| 5 | Bandai Namco Entertainment | 0.720 |

The quantitative ranking was combined with strategic feasibility considerations.

PlayStation Publishing LLC was excluded from the actionable external shortlist because it belongs to a direct platform competitor. Xbox Game Studios was excluded because it is already part of Microsoft.

The resulting focused shortlist consisted of:

1. **Valve** — primarily considered as a strategic partnership candidate;
2. **Coffee Stain Publishing** — considered as a potential acquisition candidate;
3. **CAPCOM Co., Ltd.** — considered primarily for a minority investment or strategic partnership.

These candidates exhibit different quantitative strengths rather than representing interchangeable opportunities.

Detailed results and interpretation are available in [`docs/evaluation.md`](docs/evaluation.md).


## Sensitivity Analysis

The four top-level dimension weights were varied by up to ±10 percentage points around their baseline values using 5-percentage-point increments.

A total of **625 candidate weight combinations** were generated, of which **85 valid combinations** summed to 100%.

For each valid combination, overall publisher scores were recalculated while keeping the underlying dimension scores unchanged. The analysis then examined the minimum, baseline, and maximum scores of the baseline Top 10 publishers.

The sensitivity analysis evaluates **score sensitivity rather than ranking stability**. It therefore shows how strongly numerical publisher scores depend on the weighting assumptions but does not establish whether publishers retain the same ranking positions under alternative scenarios.


## Project Structure

```text
project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── analysis/
│       ├── publisher_score_plots/
│       └── sensitivity_plots/
│
├── docs/
│   ├── preprocessing.md
│   ├── methodology.md
│   ├── evaluation.md
│   └── limitations.md
│
├── scripts/
│   ├── analysis/
│   └── preprocessing/
│
├── README.md
├── requirements.txt
└── .gitignore