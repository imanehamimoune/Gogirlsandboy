# Publisher Investment & Partnership Analysis

## Project Overview

This project develops a quantitative framework for identifying high-performing video game publishers as potential acquisition, investment, or strategic partnership candidates from Microsoft's perspective.

Game-level data from Steam and SteamSpy are cleaned, integrated, and aggregated to publisher level. Publishers are then evaluated across four performance dimensions:

- **Scale & Reach** — audience reach and language accessibility;
- **Quality** — player review performance;
- **Engagement** — continued player activity relative to estimated ownership;
- **Growth & Momentum** — recent publishing activity.

The four dimensions are combined into an overall publisher score that is used to rank eligible publishers and create a focused shortlist for further strategic and financial assessment.

The quantitative ranking is intended as a **screening and prioritization tool rather than a complete company valuation or final investment recommendation**.


## Business Context

Microsoft operates in a competitive gaming market in which publishers, intellectual property, player communities, and distribution ecosystems represent important strategic assets.

Competitors such as Sony and Tencent have used acquisitions, minority investments, and strategic partnerships to strengthen their gaming portfolios. This project examines whether publisher-level game-performance data can be used to systematically identify external publishers that may warrant further consideration by Microsoft.

The analysis addresses the following question:

> **Which established game publishers demonstrate strong and sustained performance across market reach, quality, player engagement, and recent publishing activity, and should therefore be prioritized for further strategic evaluation?**

The quantitative assessment is followed by a basic feasibility screen because a high-performing publisher is not necessarily a realistic acquisition or partnership candidate.


## Analysis Workflow

The project follows a sequential analytical pipeline:

```text
Raw data
   │
   ▼
Individual dataset preprocessing
   │
   ├── games
   ├── reviews
   ├── SteamSpy
   ├── descriptions
   └── tags / genres / categories
                 │
                 ▼
          Processed datasets
                 │
                 ▼
          Master dataset
                 │
                 ▼
      Publisher-level features
                 │
                 ▼
          Publisher scoring
                 │
                 ├── Scale & Reach
                 ├── Quality
                 ├── Engagement
                 └── Growth & Momentum
                 │
                 ▼
          Publisher ranking
             │          │
             │          └──► Publisher-score plots
             │
             ▼
       Sensitivity analysis
             │
             ▼
        Sensitivity plot
             │
             ▼
       Candidate shortlist
             │
             ▼
 Strategic & financial evaluation
```

The preprocessing scripts operate on separate source datasets and can generally be executed independently. However, all datasets required by the master-dataset construction must be processed before the merge stage.

The core analytical dependency chain is:

```text
data/processed/master_dataset.csv
              │
              ▼
build_publisher_features.py
              │
              ▼
data/processed/publisher_features.csv
              │
              ▼
build_publisher_scores.py
          │             │
          │             └──► data/analysis/publisher_score_plots/
          ▼
data/analysis/publisher_scores.csv
              │
              ▼
sensitivity_analysis_weights.py
              │
              ▼
data/analysis/sensitivity_plots/
```


## Scoring Framework

Publisher performance is evaluated across four dimensions:

| Dimension | Weight | Components |
| --- | ---: | --- |
| Scale & Reach | 35% | 80% estimated ownership, 20% language availability |
| Quality | 30% | 50% review score, 50% positive-review ratio |
| Engagement | 20% | Active-user rate |
| Growth & Momentum | 15% | 60% recent-release ratio, 40% recent-release count |
| **Total** | **100%** | |

The weights represent analytical judgments about the relative importance of the four dimensions rather than objectively determined values.

Detailed information on publisher-level aggregation, feature definitions, normalization, weighting rationale, and sensitivity design is available in [`docs/methodology.md`](docs/methodology.md).


## Key Results

After publisher-level aggregation, **814 publishers** met the requirement of being represented by at least 10 games. Complete overall scores were available for **790 publishers**.

Under the baseline scoring model, the five highest-ranked publishers were:

| Rank | Publisher | Overall Score |
| ---: | --- | ---: |
| 1 | Valve | 0.783 |
| 2 | Coffee Stain Publishing | 0.767 |
| 3 | PlayStation Publishing LLC | 0.764 |
| 4 | CAPCOM Co., Ltd. | 0.740 |
| 5 | Bandai Namco Entertainment | 0.720 |

The quantitative ranking was subsequently combined with strategic feasibility considerations.

PlayStation Publishing LLC was excluded from the actionable external shortlist because it belongs to a direct platform competitor. Xbox Game Studios was excluded because it is already part of Microsoft.

The resulting focused shortlist consisted of:

1. **Valve** — primarily considered as a strategic partnership candidate;
2. **Coffee Stain Publishing** — considered as a potential acquisition candidate;
3. **CAPCOM Co., Ltd.** — considered primarily for a minority investment or strategic partnership.

The candidates exhibit different quantitative strengths and should therefore not be interpreted as interchangeable opportunities.

Detailed results and interpretation are available in [`docs/evaluation.md`](docs/evaluation.md).


## Sensitivity Analysis

Because the baseline dimension weights represent analytical judgments, a sensitivity analysis was conducted to examine how strongly publisher scores depend on the selected top-level weights.

The four dimension weights were varied by up to ±10 percentage points around their baseline values using 5-percentage-point increments.

A total of **625 candidate weight combinations** were generated, of which **85 valid combinations** summed to 100%.

For every valid combination, overall publisher scores were recalculated while keeping the four underlying dimension scores unchanged. The baseline Top 10 publishers were selected using their original `overall_score` before examining the sensitivity results.

For each baseline Top 10 publisher, the minimum, baseline, and maximum scores across the valid weighting combinations were calculated and visualized.

The sensitivity analysis evaluates **score sensitivity rather than ranking stability**. It therefore shows how strongly numerical publisher scores depend on the weighting assumptions but does not establish whether publishers retain the same ranking positions under alternative scenarios.

See [`docs/evaluation.md`](docs/evaluation.md) for the sensitivity results.


## Project Structure

```text
project/
│
├── data/
│   ├── raw/
│   │   ├── categories.zip
│   │   ├── descriptions.zip
│   │   ├── games.zip
│   │   ├── genres.zip
│   │   ├── promotional.zip
│   │   ├── reviews.zip
│   │   ├── steamspy_insights.zip
│   │   └── tags.zip
│   │
│   ├── processed/
│   │   ├── categories_cleaned.csv
│   │   ├── categories_tags_genres_merged.csv
│   │   ├── descriptions_cleaned.zip
│   │   ├── games_cleaned.csv
│   │   ├── genres_cleaned.csv
│   │   ├── master_dataset.csv
│   │   ├── publisher_features.csv
│   │   ├── reviews_cleaned.csv
│   │   ├── steamspy_insights_cleaned.csv
│   │   └── tags_cleaned.csv
│   │
│   └── analysis/
│       ├── publisher_scores.csv
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
│   │   ├── build_publisher_features.py
│   │   ├── build_publisher_scores.py
│   │   └── sensitivity_analysis_weights.py
│   │
│   └── preprocessing/
│       ├── clean_descriptions.py
│       ├── clean_games.py
│       ├── clean_reviews.py
│       ├── clean_steamspy.py
│       ├── clean_tags_genres_categories.py
│       └── merge_datasets.py
│
├── README.md
├── requirements.txt
└── .gitignore
```


### Directory Overview

- `data/raw/` contains the original source datasets.
- `data/processed/` contains cleaned datasets, intermediate merged datasets, the final game-level master dataset, and the publisher-level feature dataset.
- `data/analysis/` contains the final publisher scores and generated analytical visualizations.
- `data/analysis/publisher_score_plots/` contains scoring visualizations automatically generated by `scripts/analysis/build_publisher_scores.py`.
- `data/analysis/sensitivity_plots/` contains the score-sensitivity visualization automatically generated by `scripts/analysis/sensitivity_analysis_weights.py`.
- `docs/` contains detailed documentation of preprocessing, methodology, evaluation, and limitations.
- `scripts/preprocessing/` contains scripts used to clean the source datasets and construct the master dataset.
- `scripts/analysis/` contains scripts used to construct publisher-level features, calculate publisher scores, generate scoring visualizations, and perform the sensitivity analysis.


## Documentation

Detailed documentation is separated according to analytical stage:

- [`docs/preprocessing.md`](docs/preprocessing.md) — data cleaning, standardization, categorical aggregation, and master-dataset construction;
- [`docs/methodology.md`](docs/methodology.md) — publisher-level aggregation, feature construction, normalization, scoring methodology, weighting rationale, and sensitivity design;
- [`docs/evaluation.md`](docs/evaluation.md) — baseline results, dimension-level findings, candidate shortlist, strategic feasibility, and score-sensitivity results;
- [`docs/limitations.md`](docs/limitations.md) — data, methodological, scoring, and business limitations.


# How to Run the Project

The project is designed as a sequential pipeline. Later analytical stages depend on outputs generated by earlier stages.

All commands below should be executed from the **project root directory**.


## 1. Clone the Repository

Clone the repository and move into the project directory:

```bash
git clone https://github.com/imanehamimoune/Gogirlsandboy.git
cd Gogirlsandboy
```


## 2. Create a Virtual Environment

Creating a virtual environment is recommended to keep the project dependencies isolated.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```


## 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```


## 4. Verify the Raw Data

Before running the preprocessing pipeline, verify that the following source files are available:

```text
data/raw/
├── categories.zip
├── descriptions.zip
├── games.zip
├── genres.zip
├── promotional.zip
├── reviews.zip
├── steamspy_insights.zip
└── tags.zip
```

The preprocessing scripts read their source files from `data/raw/`.

The raw files should remain unchanged so that the complete preprocessing pipeline can be reproduced from the original source data.


## 5. Run the Preprocessing Scripts

The individual source datasets are cleaned separately before the master dataset is constructed.

The main preprocessing sequence is:

```text
clean_games.py
clean_reviews.py
clean_steamspy.py
clean_tags_genres_categories.py
clean_descriptions.py
        │
        ▼
merge_datasets.py
        │
        ▼
master_dataset.csv
```

The first five scripts operate on separate source datasets and therefore do not necessarily depend on one another. However, the datasets required by `merge_datasets.py` must exist before the master dataset can be constructed.


### 5.1 Clean Games

Run:

```bash
python scripts/preprocessing/clean_games.py
```

**Input**

```text
data/raw/games.zip
```

**Output**

```text
data/processed/games_cleaned.csv
```

The script processes the main game-level dataset, including:

- price information;
- release dates;
- supported languages;
- full-audio support; and
- derived game-level variables.


### 5.2 Clean Reviews

Run:

```bash
python scripts/preprocessing/clean_reviews.py
```

**Input**

```text
data/raw/reviews.zip
```

**Output**

```text
data/processed/reviews_cleaned.csv
```

The script cleans and validates the review data before it is integrated into the master dataset.


### 5.3 Clean SteamSpy Data

Run:

```bash
python scripts/preprocessing/clean_steamspy.py
```

**Input**

```text
data/raw/steamspy_insights.zip
```

**Output**

```text
data/processed/steamspy_insights_cleaned.csv
```

The script processes the SteamSpy data, including:

- developer and publisher standardization;
- ownership ranges;
- price information;
- concurrent-user information; and
- derived SteamSpy variables.


### 5.4 Clean Tags, Genres, and Categories

Run:

```bash
python scripts/preprocessing/clean_tags_genres_categories.py
```

**Inputs**

```text
data/raw/tags.zip
data/raw/genres.zip
data/raw/categories.zip
```

**Outputs**

```text
data/processed/tags_cleaned.csv
data/processed/genres_cleaned.csv
data/processed/categories_cleaned.csv
data/processed/categories_tags_genres_merged.csv
```

Tags, genres, and categories initially represent many-to-many relationships because an individual game may legitimately be associated with multiple values.

The script cleans and standardizes these datasets before aggregating them to game level. The resulting combined table can therefore be integrated into the master dataset without creating multiple master-dataset rows for the same `app_id`.


### 5.5 Clean Descriptions

Run:

```bash
python scripts/preprocessing/clean_descriptions.py
```

**Input**

```text
data/raw/descriptions.zip
```

**Output**

```text
data/processed/descriptions_cleaned.zip
```

The descriptions dataset was cleaned and assessed separately.

Descriptions were ultimately not included as an analytical input because structured tags, genres, and categories were considered more suitable for the quantitative publisher analysis.

The script is retained to document the preprocessing and assessment of this source.

> `clean_descriptions.py` is not required to reproduce the final publisher scores if its output is not used by `merge_datasets.py`.


### Promotional Data

The repository also contains:

```text
data/raw/promotional.zip
```

The promotional dataset was assessed during data exploration but was not included in the final analytical pipeline. No dedicated preprocessing script is therefore required to reproduce the publisher-level results.

The rationale for excluding this source is documented in [`docs/preprocessing.md`](docs/preprocessing.md).


## 6. Construct the Master Dataset

After the required source datasets have been processed, run:

```bash
python scripts/preprocessing/merge_datasets.py
```

**Main inputs**

```text
data/processed/games_cleaned.csv
data/processed/reviews_cleaned.csv
data/processed/steamspy_insights_cleaned.csv
data/processed/categories_tags_genres_merged.csv
```

**Output**

```text
data/processed/master_dataset.csv
```

The master dataset combines the cleaned game, review, SteamSpy, and structured categorical information at game level.

It serves as the main input for the publisher-level analysis.

All required preprocessing inputs must exist before `merge_datasets.py` is executed.


## 7. Build Publisher-Level Features

After `master_dataset.csv` has been generated, run:

```bash
python scripts/analysis/build_publisher_features.py
```

**Input**

```text
data/processed/master_dataset.csv
```

**Output**

```text
data/processed/publisher_features.csv
```

This stage:

- calculates the required game-level analytical measures;
- aggregates game-level observations by publisher;
- constructs publisher-level features;
- retains established publishers represented by at least 10 games;
- normalizes the variables required for scoring; and
- validates the resulting publisher-level dataset.

Detailed feature definitions and normalization procedures are documented in [`docs/methodology.md`](docs/methodology.md).


## 8. Calculate Publisher Scores and Generate Visualizations

After `publisher_features.csv` has been generated, run:

```bash
python scripts/analysis/build_publisher_scores.py
```

**Input**

```text
data/processed/publisher_features.csv
```

**Outputs**

```text
data/analysis/publisher_scores.csv
data/analysis/publisher_score_plots/
```

The script constructs the four performance dimensions:

- **Scale & Reach**
- **Quality**
- **Engagement**
- **Growth & Momentum**

It then:

1. combines the underlying publisher features into the four dimension scores;
2. applies the baseline top-level weights;
3. calculates the overall publisher score;
4. ranks publishers with complete scores; and
5. automatically generates visualizations of the scoring results.

The resulting figures are stored in:

```text
data/analysis/publisher_score_plots/
```


## 9. Run the Sensitivity Analysis

After `publisher_scores.csv` has been generated, run:

```bash
python scripts/analysis/sensitivity_analysis_weights.py
```

**Input**

```text
data/analysis/publisher_scores.csv
```

**Output**

```text
data/analysis/sensitivity_plots/
```

The sensitivity analysis:

1. identifies the baseline Top 10 publishers using the original `overall_score`;
2. varies the four top-level dimension weights within ±10 percentage points of their baseline values using 5-percentage-point increments;
3. generates all possible combinations of the permitted weight values;
4. retains only combinations whose four weights sum to 100%;
5. recalculates publisher scores for every valid combination while keeping the underlying dimension scores unchanged;
6. determines the minimum, baseline, and maximum score for each baseline Top 10 publisher; and
7. automatically generates a visualization of these score ranges.

The sensitivity analysis evaluates **score sensitivity rather than ranking stability**.

The resulting visualization is stored in:

```text
data/analysis/sensitivity_plots/
```


## 10. Review the Results

After the complete pipeline has been executed, the main analytical outputs can be found in:

```text
data/
├── processed/
│   ├── master_dataset.csv
│   └── publisher_features.csv
│
└── analysis/
    ├── publisher_scores.csv
    ├── publisher_score_plots/
    └── sensitivity_plots/
```

Use the accompanying documentation to interpret the results:

- [`docs/evaluation.md`](docs/evaluation.md) explains the publisher ranking, individual dimension results, candidate shortlist, strategic feasibility, and score-sensitivity results.
- [`docs/limitations.md`](docs/limitations.md) explains the limitations that should be considered when interpreting the analysis.


## Execution Order Summary

| Order | Script | Main Input | Main Output |
| ---: | --- | --- | --- |
| 1 | `clean_games.py` | `games.zip` | `games_cleaned.csv` |
| 2 | `clean_reviews.py` | `reviews.zip` | `reviews_cleaned.csv` |
| 3 | `clean_steamspy.py` | `steamspy_insights.zip` | `steamspy_insights_cleaned.csv` |
| 4 | `clean_tags_genres_categories.py` | `tags.zip`, `genres.zip`, `categories.zip` | Cleaned categorical files + `categories_tags_genres_merged.csv` |
| 5 | `clean_descriptions.py` | `descriptions.zip` | `descriptions_cleaned.zip` |
| 6 | `merge_datasets.py` | Required cleaned datasets | `master_dataset.csv` |
| 7 | `build_publisher_features.py` | `master_dataset.csv` | `publisher_features.csv` |
| 8 | `build_publisher_scores.py` | `publisher_features.csv` | `publisher_scores.csv` + `publisher_score_plots/` |
| 9 | `sensitivity_analysis_weights.py` | `publisher_scores.csv` | `sensitivity_plots/` |

Steps 1–5 process separate source datasets and do not necessarily need to be executed in the order shown.

However, the subsequent dependency chain must be followed:

```text
cleaned source datasets
        ↓
master_dataset.csv
        ↓
publisher_features.csv
        ↓
publisher_scores.csv
        ↓
sensitivity analysis
```

`clean_descriptions.py` is included for documentation and completeness but is not part of the minimum pipeline required to reproduce the publisher scores if descriptions are not used by `merge_datasets.py`.

`promotional.zip` is not part of the final analytical pipeline.


## Data Sources

The analysis uses game-level information derived from Steam and SteamSpy-related datasets, including:

- games and release dates;
- publishers and developers;
- estimated ownership;
- prices;
- reviews;
- concurrent users;
- supported languages;
- tags;
- genres;
- categories; and
- descriptions.

The individual sources are cleaned separately before the required information is integrated into the game-level master dataset.

Detailed source-specific processing is documented in [`docs/preprocessing.md`](docs/preprocessing.md).


## Reproducibility

The repository separates:

- original raw data;
- processed and intermediate datasets;
- analytical outputs;
- executable scripts; and
- documentation.

Important analytical assumptions are explicitly documented, including:

- the minimum portfolio requirement of 10 games;
- treatment of missing review information;
- definition of recent releases;
- publisher-level aggregation rules;
- feature normalization methods;
- within-dimension weights;
- top-level dimension weights; and
- sensitivity-analysis ranges.

Validation checks are incorporated throughout the pipeline to identify issues such as:

- duplicate identifiers;
- missing values;
- infinite values;
- values outside expected normalization ranges;
- invalid sensitivity-weight combinations; and
- inconsistent analytical outputs.

To reproduce the analysis, users should execute the scripts from the project root and follow the dependency order documented above.


## Limitations

Several limitations should be considered when interpreting the results.

The underlying data primarily reflect the Steam and PC ecosystem and therefore do not provide a complete representation of console, mobile, or other distribution channels. SteamSpy ownership figures are estimates rather than exact sales figures, and publisher-level results are affected by missing publisher, review, and release-date information.

The scoring framework also depends on analyst-defined feature definitions, normalization procedures, eligibility criteria, and weights. The sensitivity analysis evaluates changes in numerical scores under alternative top-level weights but does not test ranking stability.

In addition, the model evaluates observed publisher performance rather than company valuation or transaction feasibility.

For these reasons, the final shortlist should be interpreted as a starting point for deeper strategic and financial due diligence rather than as a definitive acquisition recommendation.

See [`docs/limitations.md`](docs/limitations.md) for the complete discussion.


## Contributors

- Anna Andruszkiewicz
- Christian Beemelmann
- Huiying Sarah Chen
- Imane Hamimoune
- Tung-Jui Lin