''' PART 3: DOING THE SENSITIVITY ANALYSIS '''

'''
Role:
You are a senior Data Analyst and Python/Pandas expert specializing in
scoring models and sensitivity analysis. This is a minimal, purely
descriptive check — not an optimization. The goal is only to see how much
publisher scores move when the 4 top-level dimension weights are varied
within a reasonable range; it is never to search for better weights.

Context:
Input is data/analysis/publisher_scores.csv, already containing the 4
dimension scores and the existing overall_score for every publisher:
publisher_primary, scale_reach_score, quality_score, engagement_score,
momentum_score, overall_score. The baseline top-level weights are Scale &
Reach 35%, Quality 30%, Engagement 20%, Growth & Momentum 15%. Do not
recompute the 4 dimension scores or modify the input file — they're fixed
inputs. Script lives at src/feature_engineering/sensitivity_analysis.py.

Objective:
Produce exactly ONE plot — data/analysis/sensitivity_plots/
publisher_score_sensitivity.png — showing the min/baseline/max overall
score range for the baseline Top 10 publishers, across every valid
top-level weight combination in the grid below. Create the output
directory if it doesn't exist.

Tasks:
1. Load publisher_scores.csv, report its shape, and confirm all required
   columns are present (publisher_primary, overall_score, and the 4
   dimension score columns) — raise if any are missing.
2. Select the baseline Top 10 via nlargest(10, overall_score) on the
   ORIGINAL overall_score column, decided before looking at any
   sensitivity results. Never reselect the Top 10 based on scenario output.
3. Build the weight grid — each dimension varies ±10 percentage points
   around its baseline, in 5-point steps:
   - Scale & Reach: 25%–45% -> [0.25, 0.30, 0.35, 0.40, 0.45]
   - Quality: 20%–40% -> [0.20, 0.25, 0.30, 0.35, 0.40]
   - Engagement: 10%–30% -> [0.10, 0.15, 0.20, 0.25, 0.30]
   - Growth & Momentum: 5%–25% -> [0.05, 0.10, 0.15, 0.20, 0.25]
   Use these explicit hardcoded lists, not np.arange with a decimal step —
   floating-point drift (e.g. 0.39999999999997) can silently break the
   sum-to-100% check below. Generate every combination via
   itertools.product, keep only those that sum to exactly 100% — compare
   using rounded integer percentage points (round(weight * 100)), never
   raw float equality, so valid boundary values aren't rejected. The
   baseline 35/30/20/15 combination must appear in the valid set exactly
   once.
4. For every valid combination, compute each publisher's scenario score as
   the weighted sum of their EXISTING dimension scores (no recomputation):
   scenario_score = w_scale_reach * scale_reach_score
                   + w_quality * quality_score
                   + w_engagement * engagement_score
                   + w_momentum * momentum_score
5. For the baseline Top 10 only, compute min_score, the existing
   baseline_score (= their original overall_score), and max_score across
   all valid-combination scenario scores.
6. Plot (exactly one, no others): a vertical range/error-bar chart. X-axis
   = the baseline Top 10 publishers, one category each, clearly labeled
   (rotated if needed). Y-axis = score. Lower whisker = min_score, center
   marker = baseline_score, upper whisker = max_score. Clear axis labels
   and an informative title. Save to the exact path above.
7. Validate: required columns exist; every combination's weights fall
   within their stated range; every valid combination sums to 100%
   (tolerance/rounding-based, not raw float equality); no duplicate
   combinations; the baseline combination is present exactly once; and
   min_score <= baseline_score <= max_score for every Top 10 publisher.
8. Print a short summary: publisher count, candidate vs. valid combination
   counts, baseline weights, and the baseline Top 10 with their
   min/baseline/max scores and the saved plot path.

Constraints (Do Not):
- Do not recompute or alter the 4 existing dimension scores, and do not
  modify publisher_scores.csv.
- Do not search for, recommend, or imply a "better" weighting — this is
  descriptive only.
- Do not calculate rank changes, Spearman or Pearson correlations, Top-N
  overlap/stability, dimension-level sensitivity, scenario IDs, or any
  additional summary/output files.
- Do not create more than one plot.
- Do not select the Top 10 using anything other than the original,
  pre-sensitivity overall_score.
- Do not use raw floating-point equality anywhere weights are compared or
  summed — use rounding or a numerical tolerance.
- Keep the implementation concise and transparent — no unnecessary
  calculations beyond what's listed above.

Expected Output:
One script (scripts/analysis/sensitivity_analysis.py) that reads
publisher_scores.csv and produces exactly one output file —
data/analysis/sensitivity_plots/publisher_score_sensitivity.png — plus the
printed summary from Task 8. No other files created.

Keep the Python implementation concise, transparent, and reproducible.
'''

# Request: 2026-08-21 19:47 CET.
# Author: Christian Beemelmann (prompt and adjustments), ChatGPT (code and simplification)


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
