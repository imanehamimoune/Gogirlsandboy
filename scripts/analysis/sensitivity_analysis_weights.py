''' PART 3: DOING THE SENSITIVITY ANALYSIS '''

'''
Role: You are a senior Data Analyst and Python/Pandas expert specializing in scoring models, sensitivity analysis, and data visualization.

Your task is to perform a simple and reproducible sensitivity analysis for an existing publisher scoring model.

The purpose is NOT to optimize the scoring model or find better weights.

The purpose is simply to test:

How much can publisher scores change when the four top-level dimension weights are varied within a reasonable ±10 percentage-point range?

Keep the analysis simple and do not introduce unnecessary calculations.


---------------------------------------------------------------------------
1. EXISTING SCORING MODEL
---------------------------------------------------------------------------

The existing publisher scoring model consists of four top-level dimensions:

1. Scale & Reach — 35%
2. Quality — 30%
3. Engagement — 20%
4. Growth & Momentum — 15%

These four top-level weights are the only values that may change.

The internal calculations of these four dimensions have already been completed and must NOT be recalculated.

The input file already contains the four dimension scores.

The relevant columns are:

- publisher_primary
- scale_reach_score
- quality_score
- engagement_score
- momentum_score
- overall_score


---------------------------------------------------------------------------
2. INPUT AND OUTPUT
---------------------------------------------------------------------------

The relevant project structure is:

project/
│
├── data/
│   └── analysis/
│       └── publisher_scores.csv
│
└── src/
    └── feature_engineering/
        └── sensitivity_analysis.py

Read the data from:

data/analysis/publisher_scores.csv

Do not modify the input file.

Save the generated plot to:

data/analysis/sensitivity_plots/

Create the output directory automatically if it does not exist.


---------------------------------------------------------------------------
3. LOAD THE DATA
---------------------------------------------------------------------------

Load publisher_scores.csv using pandas.

Report the shape of the dataset.

Use the following columns:

Publisher:
    publisher_primary

Dimension scores:
    scale_reach_score
    quality_score
    engagement_score
    momentum_score

The existing overall_score column should be used to determine the baseline Top 10 publishers.

Do not recalculate the internal dimension scores.


---------------------------------------------------------------------------
4. WEIGHT SENSITIVITY GRID
---------------------------------------------------------------------------

Test every possible combination of the four top-level dimension weights.

Use 5-percentage-point increments.

Each dimension can vary by ±10 percentage points around its baseline:

Scale & Reach:
    25% – 45%

Quality:
    20% – 40%

Engagement:
    10% – 30%

Growth & Momentum:
    5% – 25%

Therefore, the possible values are:

Scale & Reach:
    25%, 30%, 35%, 40%, 45%

Quality:
    20%, 25%, 30%, 35%, 40%

Engagement:
    10%, 15%, 20%, 25%, 30%

Growth & Momentum:
    5%, 10%, 15%, 20%, 25%

Generate all possible combinations programmatically.

Only keep combinations where the four weights sum to exactly 100%.

Do not manually select scenarios.

The baseline combination:

35% / 30% / 20% / 15%

must be included.

IMPORTANT IMPLEMENTATION REQUIREMENT:

The weight values represent exact 5-percentage-point increments.

Avoid floating-point precision problems when generating and validating the
weight combinations.

Do NOT rely on np.arange() with decimal step sizes if this can introduce
values such as 0.39999999999999997 instead of 0.40.

Prefer explicitly defined weight values, for example:

Scale & Reach:
    [0.25, 0.30, 0.35, 0.40, 0.45]

Quality:
    [0.20, 0.25, 0.30, 0.35, 0.40]

Engagement:
    [0.10, 0.15, 0.20, 0.25, 0.30]

Growth & Momentum:
    [0.05, 0.10, 0.15, 0.20, 0.25]

When checking whether weights sum to 100%, use appropriate rounding,
numerical tolerance, or another robust method rather than relying on raw
floating-point equality.

The validation must not incorrectly reject valid boundary values because of
floating-point representation.


---------------------------------------------------------------------------
5. CALCULATE SENSITIVITY SCORES
---------------------------------------------------------------------------

For every valid weight combination, calculate an overall score for every publisher.

Use the existing dimension scores:

scenario_score =
    scale_reach_weight * scale_reach_score
    + quality_weight * quality_score
    + engagement_weight * engagement_score
    + momentum_weight * momentum_score

Only the four top-level weights change.

The underlying dimension scores remain exactly the same for every scenario.

No other calculations are required.


---------------------------------------------------------------------------
6. SELECT BASELINE TOP 10
---------------------------------------------------------------------------

Use the existing overall_score column to identify the baseline Top 10 publishers.

Do this BEFORE examining the sensitivity results.

The Top 10 publishers must therefore be determined exclusively from the original baseline scoring model.

Do not select publishers based on their sensitivity results.


---------------------------------------------------------------------------
7. CALCULATE SCORE RANGES
---------------------------------------------------------------------------

For each of the baseline Top 10 publishers, calculate:

- minimum score across all valid weight combinations
- existing baseline overall_score
- maximum score across all valid weight combinations

These values will be used for the visualization.


---------------------------------------------------------------------------
8. CREATE THE PLOT
---------------------------------------------------------------------------

Create exactly ONE plot.

The plot should show the score sensitivity of the baseline Top 10 publishers.

Use a vertical range/error-bar style visualization:

- X-axis = publisher
- Y-axis = publisher score
- lower end of the error bar = minimum score
- central point = baseline overall_score
- upper end of the error bar = maximum score

Each publisher should appear as one category on the X-axis.

The purpose of the visualization is to show how much each publisher's score can
change when the top-level dimension weights are varied within the defined
sensitivity ranges.

Use:

- clear publisher labels on the X-axis
- a clearly labelled Y-axis
- an informative title
- readable formatting
- appropriate rotation of publisher labels if necessary

Save the plot as:

data/analysis/sensitivity_plots/publisher_score_sensitivity.png

Do not create any other plots.


---------------------------------------------------------------------------
9. VALIDATION
---------------------------------------------------------------------------

Perform only the following basic validation:

- confirm that all required columns exist
- confirm that all generated weight combinations are within their specified ranges
- confirm that every valid combination sums to 100%
- confirm that there are no duplicate combinations
- confirm that the baseline 35/30/20/15 combination is included
- confirm that minimum score <= baseline score <= maximum score
- ensure that floating-point representation does not cause valid weight
  combinations or boundary values to fail validation
- use rounding, numerical tolerance, or another robust method where
  appropriate when comparing decimal weights

Print a short summary containing:

- number of publishers
- total candidate combinations
- number of valid combinations
- baseline weights
- baseline Top 10 publishers
- minimum, baseline, and maximum score for each Top 10 publisher
- location of the generated plot


---------------------------------------------------------------------------
10. CONSTRAINTS
---------------------------------------------------------------------------

Keep the analysis simple.

Do NOT:

- optimize the weights
- search for a best weighting scheme
- analyze ranking stability
- calculate rank changes
- calculate Spearman correlations
- calculate Pearson correlations
- calculate Top-N stability
- perform dimension-level sensitivity analysis
- create scenario IDs
- create additional scenario summary files
- recalculate the internal dimension scores
- redo feature engineering
- modify publisher_scores.csv
- introduce additional mathematical analyses
- create unnecessary output files

The only purpose of the script is:

1. Generate all valid top-level weight combinations within the ±10 percentage-point ranges.
2. Calculate the resulting publisher scores.
3. Take the baseline Top 10 publishers.
4. Determine their minimum, baseline, and maximum scores.
5. Create one sensitivity plot.

Keep the Python implementation concise, transparent, and reproducible.
'''

# Request: 2026-08-21 19:47 CET.
# Author: Christian Beemelmann (prompt and adjustments), ChatGPT (simplification)


# =============================================================================
# PART 3: PUBLISHER SCORE SENSITIVITY ANALYSIS
# =============================================================================

from pathlib import Path
import itertools

import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# 1. CONFIGURATION
# =============================================================================

INPUT_PATH = Path("data/analysis/publisher_scores.csv")
OUTPUT_DIR = Path("data/analysis/sensitivity_plots")
OUTPUT_PATH = OUTPUT_DIR / "publisher_score_sensitivity.png"

PUBLISHER_COLUMN = "publisher_primary"
OVERALL_SCORE_COLUMN = "overall_score"

DIMENSION_COLUMNS = {
    "scale_reach": "scale_reach_score",
    "quality": "quality_score",
    "engagement": "engagement_score",
    "momentum": "momentum_score",
}

BASELINE_WEIGHTS = {
    "scale_reach": 0.35,
    "quality": 0.30,
    "engagement": 0.20,
    "momentum": 0.15,
}

# Explicit values are used to avoid floating-point problems.
WEIGHT_VALUES = {
    "scale_reach": [0.25, 0.30, 0.35, 0.40, 0.45],
    "quality": [0.20, 0.25, 0.30, 0.35, 0.40],
    "engagement": [0.10, 0.15, 0.20, 0.25, 0.30],
    "momentum": [0.05, 0.10, 0.15, 0.20, 0.25],
}

TOP_N = 10


# =============================================================================
# 2. LOAD DATA
# =============================================================================

print("=" * 70)
print("LOAD DATA")
print("=" * 70)

df = pd.read_csv(INPUT_PATH)

print(f"Input file: {INPUT_PATH}")
print(f"Dataset shape: {df.shape}")


# =============================================================================
# 3. VALIDATE REQUIRED COLUMNS
# =============================================================================

required_columns = [
    PUBLISHER_COLUMN,
    OVERALL_SCORE_COLUMN,
    *DIMENSION_COLUMNS.values(),
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("All required columns are available.")


# =============================================================================
# 4. SELECT BASELINE TOP 10
# =============================================================================

print("\n" + "=" * 70)
print("BASELINE TOP 10")
print("=" * 70)

top10 = (
    df.nlargest(TOP_N, OVERALL_SCORE_COLUMN)
    .copy()
)

print(
    top10[
        [PUBLISHER_COLUMN, OVERALL_SCORE_COLUMN]
    ].to_string(index=False)
)


# =============================================================================
# 5. GENERATE ALL VALID WEIGHT COMBINATIONS
# =============================================================================

print("\n" + "=" * 70)
print("GENERATE WEIGHT COMBINATIONS")
print("=" * 70)

dimensions = list(BASELINE_WEIGHTS.keys())

candidate_combinations = list(
    itertools.product(
        WEIGHT_VALUES["scale_reach"],
        WEIGHT_VALUES["quality"],
        WEIGHT_VALUES["engagement"],
        WEIGHT_VALUES["momentum"],
    )
)

valid_combinations = []

for combination in candidate_combinations:

    # Convert weights to integer percentage points.
    # This completely avoids floating-point precision problems.
    percentage_points = [
        round(weight * 100)
        for weight in combination
    ]

    if sum(percentage_points) == 100:
        valid_combinations.append(combination)

print(
    f"Total candidate combinations: "
    f"{len(candidate_combinations)}"
)

print(
    f"Valid combinations: "
    f"{len(valid_combinations)}"
)


# =============================================================================
# 6. VALIDATE WEIGHT COMBINATIONS
# =============================================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

# Check for duplicate combinations.
assert len(valid_combinations) == len(set(valid_combinations)), (
    "Duplicate weight combinations found."
)

# Check that every valid combination sums to exactly 100%.
assert all(
    sum(round(weight * 100) for weight in combination) == 100
    for combination in valid_combinations
), "A weight combination does not sum to 100%."

# Check that all weights are within the specified ranges.
for combination in valid_combinations:

    for weight, dimension in zip(combination, dimensions):

        assert weight in WEIGHT_VALUES[dimension], (
            f"Invalid weight {weight} for {dimension}."
        )

# Check that the baseline combination occurs exactly once.
baseline_combination = tuple(
    BASELINE_WEIGHTS[dimension]
    for dimension in dimensions
)

baseline_count = valid_combinations.count(
    baseline_combination
)

assert baseline_count == 1, (
    f"Baseline combination occurs {baseline_count} times."
)

print("All weight combinations are valid.")
print("No duplicate combinations found.")
print("Every valid combination sums to 100%.")
print(
    "Baseline 35% / 30% / 20% / 15% "
    "combination found exactly once."
)


# =============================================================================
# 7. CALCULATE SENSITIVITY SCORES
# =============================================================================

print("\n" + "=" * 70)
print("CALCULATE SENSITIVITY SCORES")
print("=" * 70)

scenario_scores = []

for combination in valid_combinations:

    weights = dict(
        zip(dimensions, combination)
    )

    score = (
        weights["scale_reach"]
        * df[DIMENSION_COLUMNS["scale_reach"]]
        + weights["quality"]
        * df[DIMENSION_COLUMNS["quality"]]
        + weights["engagement"]
        * df[DIMENSION_COLUMNS["engagement"]]
        + weights["momentum"]
        * df[DIMENSION_COLUMNS["momentum"]]
    )

    scenario_scores.append(score)


scenario_scores = pd.concat(
    scenario_scores,
    axis=1
)

print(
    f"Calculated scores for "
    f"{len(valid_combinations)} valid weight combinations."
)


# =============================================================================
# 8. CALCULATE SCORE RANGES FOR BASELINE TOP 10
# =============================================================================

top10_scenario_scores = scenario_scores.loc[top10.index]

top10["min_score"] = top10_scenario_scores.min(axis=1)
top10["max_score"] = top10_scenario_scores.max(axis=1)

# Use the existing overall_score as the baseline score.
top10["baseline_score"] = top10[OVERALL_SCORE_COLUMN]


# Validate score ranges.
assert (
    (top10["min_score"] <= top10["baseline_score"])
    & (top10["baseline_score"] <= top10["max_score"])
).all(), (
    "At least one baseline score is outside "
    "its calculated minimum/maximum range."
)

print(
    "Minimum, baseline, and maximum scores "
    "calculated successfully."
)


# =============================================================================
# 9. CREATE PLOT
# =============================================================================

print("\n" + "=" * 70)
print("CREATE PLOT")
print("=" * 70)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Sort by baseline score so the highest-ranked publisher
# appears on the left.
plot_data = (
    top10
    .sort_values("baseline_score", ascending=False)
    .reset_index(drop=True)
)

x_positions = range(len(plot_data))

lower_error = (
    plot_data["baseline_score"]
    - plot_data["min_score"]
)

upper_error = (
    plot_data["max_score"]
    - plot_data["baseline_score"]
)

plt.figure(figsize=(12, 7))

plt.errorbar(
    x_positions,
    plot_data["baseline_score"],
    yerr=[
        lower_error,
        upper_error,
    ],
    fmt="o",
    capsize=5,
)

plt.xticks(
    list(x_positions),
    plot_data[PUBLISHER_COLUMN],
    rotation=45,
    ha="right",
)

plt.xlabel("Publisher")
plt.ylabel("Publisher Score")

plt.title(
    "Publisher Score Sensitivity to Top-Level Dimension Weights"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Plot saved to: {OUTPUT_PATH}")


# =============================================================================
# 10. SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"Number of publishers: {len(df)}")
print(
    f"Total candidate combinations: "
    f"{len(candidate_combinations)}"
)
print(
    f"Valid combinations: "
    f"{len(valid_combinations)}"
)

print("\nBaseline weights:")

for dimension, weight in BASELINE_WEIGHTS.items():
    print(
        f"  {dimension:15s}: {weight:.0%}"
    )

print("\nBaseline Top 10 score sensitivity:")

summary = (
    top10[
        [
            PUBLISHER_COLUMN,
            "min_score",
            "baseline_score",
            "max_score",
        ]
    ]
    .sort_values(
        "baseline_score",
        ascending=False
    )
)

print(
    summary.to_string(index=False)
)

print(f"\nPlot saved to: {OUTPUT_PATH}")
print("\nSensitivity analysis completed successfully.")
