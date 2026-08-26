# Publisher Investment & Partnership Analysis

## Overview

This project develops a quantitative framework for identifying high-performing video game publishers as potential acquisition, investment, or strategic partnership candidates from Microsoft's perspective.

Game-level data from Steam and SteamSpy are cleaned, integrated, and aggregated to publisher level. Publishers are then evaluated across four performance dimensions:

| Dimension             | Purpose                                                   |
| --------------------- | --------------------------------------------------------- |
| **Scale & Reach**     | Audience reach and language accessibility                 |
| **Quality**           | Player review performance                                 |
| **Engagement**        | Continued player activity relative to estimated ownership |
| **Growth & Momentum** | Recent publishing activity                                |

The four dimensions are combined into an overall publisher score used to rank eligible publishers and create a focused shortlist for further strategic and financial assessment.

The quantitative ranking is intended as a **screening and prioritization tool rather than a complete company valuation or final investment recommendation**.

---

## Business Question

Microsoft operates in a competitive gaming market in which publishers, intellectual property, player communities, and distribution ecosystems represent important strategic assets.

Competitors such as Sony and Tencent have used acquisitions, minority investments, and strategic partnerships to strengthen their gaming portfolios.

This project examines whether publisher-level game-performance data can be used to systematically identify external publishers that may warrant further consideration by Microsoft.

The analysis addresses the following question:

> **Which established game publishers demonstrate strong and sustained performance across market reach, quality, player engagement, and recent publishing activity, and should therefore be prioritized for further strategic evaluation?**

The quantitative assessment is followed by a basic feasibility screen because a high-performing publisher is not necessarily a realistic acquisition or partnership candidate.

---

## Analysis Workflow

The project follows a sequential analytical pipeline:

```text
Raw datasets
     │
     ▼
Dataset preprocessing
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
     │
     ├── Publisher-score plots
     │
     ▼
Sensitivity analysis
     │
     └── Sensitivity plot
     │
     ▼
Candidate shortlist
     │
     ▼
Strategic & financial evaluation
```

The preprocessing scripts operate on separate source datasets and can generally be executed independently. All datasets required for master-dataset construction must, however, be processed before the merge stage.

The main analytical dependency chain is:

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
              │
              ├──► data/analysis/publisher_score_plots/
              │
              ▼
data/analysis/publisher_scores.csv
              │
              ▼
sensitivity_analysis_weights.py
              │
              ▼
data/analysis/sensitivity_plots/
```

---

## Scoring Framework

Publisher performance is evaluated across four dimensions:

| Dimension         | Overall Weight | Components                                         |
| ----------------- | -------------: | -------------------------------------------------- |
| Scale & Reach     |            35% | 80% estimated ownership, 20% language availability |
| Quality           |            30% | 50% review score, 50% positive-review ratio        |
| Engagement        |            20% | Active-user rate                                   |
| Growth & Momentum |            15% | 60% recent-release ratio, 40% recent-release count |
| **Total**         |       **100%** |                                                    |

The weights represent analytical judgments about the relative importance of the four dimensions rather than objectively determined values.

Detailed information on publisher-level aggregation, feature definitions, normalization, weighting rationale, and sensitivity design is available in [`docs/methodology.md`](docs/methodology.md).

---

## Key Results

After publisher-level aggregation:

* **814 publishers** met the requirement of being represented by at least 10 games.
* **790 publishers** had complete overall scores.

### Baseline Top 5

| Rank | Publisher                  | Overall Score |
| ---: | -------------------------- | ------------: |
|    1 | Valve                      |         0.783 |
|    2 | Coffee Stain Publishing    |         0.767 |
|    3 | PlayStation Publishing LLC |         0.764 |
|    4 | CAPCOM Co., Ltd.           |         0.740 |
|    5 | Bandai Namco Entertainment |         0.720 |

The quantitative ranking was subsequently combined with strategic feasibility considerations.

PlayStation Publishing LLC was excluded from the actionable external shortlist because it belongs to a direct platform competitor. Xbox Game Studios was excluded because it is already part of Microsoft.

### Candidate Shortlist

| Candidate                   | Strategic Interpretation                                                |
| --------------------------- | ----------------------------------------------------------------------- |
| **Valve**                   | Primarily considered as a strategic partnership candidate               |
| **Coffee Stain Publishing** | Considered as a potential acquisition candidate                         |
| **CAPCOM Co., Ltd.**        | Considered primarily for a minority investment or strategic partnership |

The candidates exhibit different quantitative strengths and should not be interpreted as interchangeable opportunities.

Detailed results, candidate comparisons, and interpretation are available in [`docs/evaluation.md`](docs/evaluation.md).

---

## Note on Presented Results

The publisher rankings reported in this repository may differ slightly from those shown in the project presentation.

After the presentation was prepared, an issue was identified in the analysis code that affected the calculation of the publisher-level scores. The issue was corrected, and the publisher features, scores, rankings, visualizations, and sensitivity analysis were regenerated using the corrected implementation.

As a result, some publishers changed position slightly compared with the rankings presented during the lectures. The results contained in this repository represent the **final corrected version of the analysis** and should therefore be treated as authoritative.

The correction did not change the overall analytical framework, performance dimensions, or interpretation of the scoring methodology.

---

## Sensitivity Analysis

Because the baseline dimension weights represent analytical judgments, a sensitivity analysis was conducted to examine how strongly publisher scores depend on the selected top-level weights.

The four dimension weights were varied by up to **±10 percentage points** around their baseline values using **5-percentage-point increments**.

This produced:

* **625 candidate weight combinations**;
* **85 valid combinations** whose four weights summed to 100%.

For every valid combination, overall publisher scores were recalculated while keeping the four underlying dimension scores unchanged.

The baseline Top 10 publishers were selected using their original `overall_score` before examining the sensitivity results. For each publisher, the minimum, baseline, and maximum scores across the valid weighting combinations were calculated and visualized.

The sensitivity analysis evaluates **score sensitivity rather than ranking stability**. It shows how strongly numerical publisher scores depend on the weighting assumptions but does not establish whether publishers retain the same ranking positions under alternative scenarios.

See [`docs/evaluation.md`](docs/evaluation.md) for the sensitivity results.

---

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
│   │   ├── sensitivity_analysis_weights.py
│   │   └── run_analysis_pipeline.sh
│   │
│   └── preprocessing/
│       ├── clean_descriptions.py
│       ├── clean_games.py
│       ├── clean_reviews.py
│       ├── clean_steamspy.py
│       ├── clean_tags_genres_categories.py
│       ├── merge_datasets.py
│       └── run_preprocessing_pipeline.sh
│
├── README.md
├── requirements.txt
└── .gitignore
```

### Directory Overview

| Directory                              | Contents                                                                                 |
| -------------------------------------- | ---------------------------------------------------------------------------------------- |
| `data/raw/`                            | Original source datasets                                                                 |
| `data/processed/`                      | Cleaned datasets, intermediate datasets, master dataset, and publisher-level features    |
| `data/analysis/`                       | Publisher scores and analytical visualizations                                           |
| `data/analysis/publisher_score_plots/` | Visualizations generated by `build_publisher_scores.py`                                  |
| `data/analysis/sensitivity_plots/`     | Score-sensitivity visualization generated by `sensitivity_analysis_weights.py`           |
| `scripts/preprocessing/`               | Data cleaning and master-dataset construction scripts                                    |
| `scripts/analysis/`                    | Publisher feature construction, scoring, visualization, and sensitivity-analysis scripts |
| `scripts/preprocessing/run_preprocessing_pipeline.sh` | Executes the required preprocessing pipeline in the correct order |
| `scripts/analysis/run_analysis_pipeline.sh` | Executes the publisher-level analysis and sensitivity pipeline in the correct order |
| `docs/`                                | Detailed analytical documentation                                                        |

---

## Documentation

Detailed documentation is separated by analytical stage:

| Document                                         | Contents                                                                                                         |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| [`docs/preprocessing.md`](docs/preprocessing.md) | Data cleaning, standardization, categorical aggregation, and master-dataset construction                         |
| [`docs/methodology.md`](docs/methodology.md)     | Publisher aggregation, feature construction, normalization, scoring, weighting rationale, and sensitivity design |
| [`docs/evaluation.md`](docs/evaluation.md)       | Baseline results, dimension-level findings, candidate shortlist, strategic feasibility, and score sensitivity    |
| [`docs/limitations.md`](docs/limitations.md)     | Data, methodological, scoring, and business limitations                                                          |

---

# How to Run the Project

The project is designed as a sequential pipeline. Later analytical stages depend on outputs generated by earlier stages.

Run all commands from the **project root directory**.

## 1. Clone the Repository

```bash
git clone https://github.com/imanehamimoune/Gogirlsandboy.git
cd Gogirlsandboy
```

## 2. Create a Virtual Environment

Creating a virtual environment is recommended to keep project dependencies isolated.

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

---

## 5. Run the Complete Pipeline

The recommended way to reproduce the complete analysis is to use the provided shell pipeline scripts. These scripts execute the required Python scripts in the correct dependency order.

### Step 1: Preprocessing

Run:

```bash
bash scripts/preprocessing/run_preprocessing_pipeline.sh
```

This executes the required preprocessing stages and constructs:

```text
data/processed/master_dataset.csv
```

The expected master-dataset shape is:

```text
140,082 rows × 68 columns
```

This can be used as a reproducibility check after preprocessing.

### Step 2: Analysis

After preprocessing has completed successfully, run:

```bash
bash scripts/analysis/run_analysis_pipeline.sh
```

This executes the publisher-level analysis and produces:

```text
data/processed/publisher_features.csv

data/analysis/
├── publisher_scores.csv
├── publisher_score_plots/
└── sensitivity_plots/
```

The complete recommended execution sequence is therefore:

```text
data/raw/
    │
    ▼
run_preprocessing_pipeline.sh
    │
    ▼
master_dataset.csv
    │
    ▼
run_analysis_pipeline.sh
    │
    ├──► publisher_features.csv
    ├──► publisher_scores.csv
    ├──► publisher_score_plots/
    └──► sensitivity_plots/
```

The individual Python scripts can also be executed manually as documented in the following sections.

---

## 6. Preprocess the Source Data

The source datasets are cleaned separately before the master dataset is constructed.

### Required Preprocessing Scripts

| Script                            | Input                                      | Main Output                                                        |
| --------------------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| `clean_games.py`                  | `games.zip`                                | `games_cleaned.csv`                                                |
| `clean_reviews.py`                | `reviews.zip`                              | `reviews_cleaned.csv`                                              |
| `clean_steamspy.py`               | `steamspy_insights.zip`                    | `steamspy_insights_cleaned.csv`                                    |
| `clean_tags_genres_categories.py` | `tags.zip`, `genres.zip`, `categories.zip` | Cleaned categorical datasets + `categories_tags_genres_merged.csv` |

These scripts operate on separate source datasets and do not depend on one another.

### Clean Games

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

The script processes:

- price information, retaining price fields only where the reported currency is EUR;
- release dates;
- supported languages;
- full-audio support; and
- derived game-level variables.

Games with non-EUR price information are retained in the dataset, but their extracted price-related fields are treated as missing rather than converted across currencies.

### Clean Reviews

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

The script cleans and validates the review data before integration into the master dataset.

### Clean SteamSpy Data

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

The script processes:

* developer and publisher information;
* ownership ranges;
* price information;
* concurrent-user information; and
* derived SteamSpy variables.

### Clean Tags, Genres, and Categories

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

The script cleans and standardizes these datasets before aggregating them to game level. The resulting combined table can therefore be integrated into the master dataset without creating multiple rows for the same `app_id`.

### Optional: Clean Descriptions

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

The descriptions dataset was cleaned and assessed separately but was ultimately not included as an analytical input because structured tags, genres, and categories were considered more suitable for the quantitative publisher analysis.

The script is retained to document the preprocessing and assessment of this source.

> `clean_descriptions.py` is not required to reproduce the final publisher scores if its output is not used by `merge_datasets.py`.

### Promotional Data

`data/raw/promotional.zip` was assessed during data exploration but was not included in the final analytical pipeline.

No dedicated preprocessing script is required to reproduce the publisher-level results.

The rationale for excluding descriptions and promotional information is documented in [`docs/preprocessing.md`](docs/preprocessing.md).

---

## 7. Construct the Master Dataset

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

The resulting master dataset contains **140,082 rows and 68 columns**, with each row representing a game-level observation identified by `app_id`.

This expected shape can be used as a reproducibility check when rerunning the preprocessing pipeline.

---

## 8. Build Publisher-Level Features

Run:

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

* calculates the required game-level analytical measures;
* aggregates game-level observations by publisher;
* constructs publisher-level features;
* retains established publishers represented by at least 10 games;
* normalizes variables required for scoring; and
* validates the resulting publisher-level dataset.

Detailed feature definitions and normalization procedures are documented in [`docs/methodology.md`](docs/methodology.md).

---

## 9. Calculate Publisher Scores

Run:

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

The script:

1. constructs Scale & Reach, Quality, Engagement, and Growth & Momentum;
2. applies the baseline top-level weights;
3. calculates the overall publisher score;
4. ranks publishers with complete scores; and
5. generates visualizations of the scoring results.

---

## 10. Run the Sensitivity Analysis

Run:

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
2. varies the four top-level weights within ±10 percentage points of their baseline values using 5-percentage-point increments;
3. generates all permitted weight combinations;
4. retains combinations whose four weights sum to 100%;
5. recalculates publisher scores while keeping the underlying dimension scores unchanged;
6. determines the minimum, baseline, and maximum score for each baseline Top 10 publisher; and
7. generates a visualization of the resulting score ranges.

The analysis evaluates **score sensitivity rather than ranking stability**.

---

## 11. Review the Outputs

The main analytical outputs are:

| Output                                  | Purpose                                                 |
| --------------------------------------- | ------------------------------------------------------- |
| `data/processed/master_dataset.csv`     | Final game-level analytical dataset                     |
| `data/processed/publisher_features.csv` | Publisher-level features used for scoring               |
| `data/analysis/publisher_scores.csv`    | Dimension scores, overall scores, and publisher ranking |
| `data/analysis/publisher_score_plots/`  | Publisher-scoring visualizations                        |
| `data/analysis/sensitivity_plots/`      | Score-sensitivity visualization                         |

Use [`docs/evaluation.md`](docs/evaluation.md) to interpret the publisher ranking, individual dimensions, candidate shortlist, strategic feasibility, and sensitivity results.

Use [`docs/limitations.md`](docs/limitations.md) for the limitations that should be considered when interpreting the analysis.

---

## Execution Order

### Recommended Execution

The complete pipeline can be reproduced using two shell scripts:

```bash
bash scripts/preprocessing/run_preprocessing_pipeline.sh
bash scripts/analysis/run_analysis_pipeline.sh
```

The analysis pipeline should only be executed after the preprocessing pipeline has completed successfully.

### Manual Execution

For users who want to execute or inspect each stage individually, the dependency chain is:

```text
Required source preprocessing
          │
          ▼
master_dataset.csv
          │
          ▼
publisher_features.csv
          │
          ▼
publisher_scores.csv
          │
          ▼
sensitivity analysis
```

The preprocessing scripts for games, reviews, SteamSpy, and tags/genres/categories operate independently and can be executed in any order before `merge_datasets.py`.

| Stage | Script                            | Main Output                                  |
| ----: | --------------------------------- | -------------------------------------------- |
|     1 | `clean_games.py`                  | `games_cleaned.csv`                          |
|     2 | `clean_reviews.py`                | `reviews_cleaned.csv`                        |
|     3 | `clean_steamspy.py`               | `steamspy_insights_cleaned.csv`              |
|     4 | `clean_tags_genres_categories.py` | Cleaned categorical files + aggregated table |
|     5 | `merge_datasets.py`               | `master_dataset.csv`                         |
|     6 | `build_publisher_features.py`     | `publisher_features.csv`                     |
|     7 | `build_publisher_scores.py`       | `publisher_scores.csv` + scoring plots       |
|     8 | `sensitivity_analysis_weights.py` | Sensitivity plot                             |

`clean_descriptions.py` is retained for documentation and completeness but is not part of the minimum pipeline required to reproduce the publisher scores if descriptions are not used by `merge_datasets.py`.

`promotional.zip` is not part of the final analytical pipeline.

---

## Data Sources

The analysis uses game-level information derived from Steam and SteamSpy-related datasets, including:

* games and release dates;
* publishers and developers;
* estimated ownership;
* prices;
* reviews;
* concurrent users;
* supported languages;
* tags;
* genres; and
* categories.

The individual sources are cleaned separately before the required information is integrated into the game-level master dataset.

Detailed source-specific processing is documented in [`docs/preprocessing.md`](docs/preprocessing.md).

---

## Reproducibility

The repository separates:

* original raw data;
* processed and intermediate datasets;
* analytical outputs;
* executable scripts; and
* documentation.

Important analytical assumptions are explicitly documented, including:

* the minimum portfolio requirement of 10 games;
* treatment of missing review information;
* definition of recent releases;
* publisher-level aggregation rules;
* feature normalization methods;
* within-dimension weights;
* top-level dimension weights; and
* sensitivity-analysis ranges.

Validation checks are incorporated throughout the pipeline for:

* duplicate identifiers;
* missing values;
* infinite values;
* values outside expected normalization ranges;
* invalid sensitivity-weight combinations; and
* inconsistent analytical outputs.

To reproduce the analysis, execute the scripts from the project root and follow the dependency order documented above.

---

## Use of Generative AI

Generative AI tools were used to assist with portions of the code development and documentation. The tools used included **GPT-5.6 Sol (OpenAI)** and **Claude Sonnet 5 (Anthropic)**.

AI assistance was used for tasks such as supporting code development, refining validation procedures, improving code documentation, and assisting with the structure and wording of project documentation.

AI-generated outputs were reviewed and adjusted by the project team before being incorporated into the final pipeline. Analytical decisions, preprocessing criteria, feature definitions, weighting assumptions, and interpretation of the results remained the responsibility of the project team.

Further details are provided in the relevant preprocessing and methodology documentation.

---

## Limitations

The analysis is subject to several data and methodological limitations.

In particular:

* the underlying data primarily reflect the Steam and PC ecosystem;
* SteamSpy ownership figures are estimates rather than exact sales figures;
* publisher-level results are affected by missing publisher, review, and release-date information;
* the scoring framework depends on analyst-defined feature definitions, normalization procedures, eligibility criteria, and weights;
* the sensitivity analysis evaluates numerical score variation rather than ranking stability; and
* the model evaluates observed publisher performance rather than company valuation or transaction feasibility.

The final shortlist should therefore be interpreted as a **starting point for deeper strategic and financial due diligence rather than a definitive acquisition recommendation**.

See [`docs/limitations.md`](docs/limitations.md) for the complete discussion.

---

## Contributors

* Anna Andruszkiewicz
* Christian Beemelmann
* Huiying Sarah Chen
* Imane Hamimoune
* Tung-Jui Lin
