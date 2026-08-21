''' PART 1: BUILDING PUBLISHER FEATURES '''

'''
Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a publisher-level feature table from game-level data. Prioritize correct, well-justified aggregation and normalization over cleverness.
Context: Input is master_dataset.csv — one row per app_id, already merged and cleaned. The next step is to aggregate this to one row per primary_publisher, producing a small set of features usable for ranking/scoring publishers. Some of these features are already naturally bounded ratios; others are raw counts/rates that need normalization before they can be compared or combined meaningfully.

Objective: Produce publisher_features.csv — one row per primary_publisher — containing exactly the 8 features below, with publishers below a minimum game count excluded, and the appropriate features normalized. Do not touch master_dataset.csv itself.
Scope decision to state explicitly (in a code comment) before proceeding:
* Propose and justify a normalization scale (log transform, min-max, or an alternative such as percentile rank) for each feature that needs one, based on that feature's own distribution — not assumed. Compute skew (or another shape diagnostic) on the actual aggregated data to justify the choice, rather than picking a method up front and hoping it fits.
Features (all aggregated per publisher):
1. review_score — mean of review_score (0-9 scale), EXCLUDING 0 values from the average. A 0 signals "too few reviews to compute a score," not an actually bad score — including it would wrongly drag a publisher's average down for being under-reviewed, not disliked.
2. owner_mid count — mean of owners_mid per publisher (reach per game).
3. language_count — mean of language_count per publisher (localization reach).
4. positive review ratio — mean of positive / (positive + negative) per game. Already bounded 0-1. Games with zero total reviews are NaN and excluded from the mean, not treated as 0% positive.
5. active users rate — mean of concurrent_users_yesterday / owners_mid per game. Conceptually a 0-1 ratio, but verify this empirically rather than assuming it — guard against division by zero (owners_mid == 0 -> NaN, not 0 or inf).
6. recent release count — count of games released within a defined "recent" window (e.g. within 2 years of the dataset's own max release_date, used as a fixed reference "today" rather than the real current date, since the data is a fixed snapshot).
7. recent release ratio — recent_release_count / game_count. Already bounded 0-1.
8. game_count — count of games per publisher (portfolio size).

Tasks:
1. Load master_dataset.csv and report its shape.
2. Per-game prep (before aggregating):
    * Compute positive_review_ratio and active_users_rate per game, guarding every division against a zero denominator (-> NaN, never 0 or inf).
    * Parse release_date; compute is_recent per game against the reference "today" described above.
    * Replace review_score == 0 with NaN for averaging purposes only (do not alter the underlying review_score column's meaning elsewhere).
    * Report how many rows have a missing primary_publisher (these can't be aggregated — exclude them from this table, don't guess a publisher).
3. Aggregate to publisher level using the 8 feature definitions above.
4. Drop publishers with game_count < 10. Report publisher count before and after this filter.
5. Normalize the count/rate features (owner_mid count, language_count, game_count, recent_release_count, active_users_rate) using the scale proposed and justified in the scope decision above, writing results to NEW columns (e.g. <feature>_norm) — never overwrite the original. Leave review_score, positive_review_ratio, and recent_release_ratio unnormalized, since they're already bounded and directly interpretable.
6. Execute and validate:
    * Actually run the code.
    * Confirm: one row per publisher, no duplicate publishers, no inf/-inf values anywhere (check explicitly), and report missing % per column.
7. Deliver:
    * The code, plus a short summary: publisher count before/after the game_count filter, the normalization method chosen per feature (with the diagnostic that justified it), and which columns have the most missingness and why.

Constraints (Do Not):
* Do not drop any game-level row for reasons other than missing primary_publisher (which can't be aggregated at all).
* Do not fill a NaN ratio/average with 0 — a 0 has a different meaning (e.g. "no reviews at all") than "not enough data to compute."
* Do not silently let divide-by-zero produce inf — guard explicitly.
* Do not normalize review_score, positive_review_ratio, or recent_release_ratio — they're already bounded and interpretable as-is.
* Do not pick a normalization method without first checking the actual distribution of that feature on this data.
* Do not overengineer — no scaling/encoding beyond what's needed for the 5 count/rate features, no speculative extra features.

Expected Output:
* publisher_features.csv: one row per primary_publisher (game_count >= 10 only), containing the 8 requested features plus normalized (_norm) versions of owner_mid count, language_count, game_count, recent_release_count, and active_users_rate.
* A short written summary covering: publisher counts before/after filtering, the normalization method and justification per feature, and notable missingness patterns.

Validation:
* Reload the output and confirm: no duplicate publishers, all publishers have game_count >= 10, no inf/-inf values anywhere, and normalized columns fall within their expected range (e.g. [0,1] for min-max-based methods).

'''
# Request: 2026-08-20 19:50 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


"""
Build publisher_features.csv from master_dataset.csv: one row per
primary_publisher, aggregating game-level data into 8 features. Publishers
with fewer than MIN_GAMES titles are dropped.

Structured to follow the task numbering in the source prompt (Tasks 1-7)
so each section below maps directly back to it.
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "data/processed/master_dataset.csv"
OUT = "data/feature_analysis/publisher_features.csv"
MIN_GAMES = 10
RECENT_YEARS = 2

# =============================================================================
# TASK 1: LOAD
# =============================================================================
df = pd.read_csv(SRC, low_memory=False)
print("=" * 70)
print("TASK 1: LOAD")
print("=" * 70)
print("Loaded master_dataset.csv:", df.shape)

# =============================================================================
# TASK 2: PER-GAME PREP (before aggregating)
# =============================================================================
print("\n" + "=" * 70)
print("TASK 2: PER-GAME PREP")
print("=" * 70)

# positive_review_ratio and active_users_rate -- guard every division
# against a zero denominator (-> NaN, never 0 or inf)
review_denom = df["positive"] + df["negative"]
df["review_positive_ratio"] = np.where(review_denom > 0, df["positive"] / review_denom, np.nan)
df["active_users_rate"] = np.where(df["owners_mid"] > 0, df["concurrent_users_yesterday"] / df["owners_mid"], np.nan)
print("Computed review_positive_ratio and active_users_rate (both NaN-guarded against division by zero).")

# parse release_date; compute is_recent against a fixed reference "today"
# (the dataset's own max release_date, not the real current date, since
# this is a fixed snapshot)
df["release_date_parsed"] = pd.to_datetime(df["release_date"], errors="coerce")
reference_today = df["release_date_parsed"].max()
df["is_recent"] = (reference_today - df["release_date_parsed"]).dt.days / 365.25 <= RECENT_YEARS
print(f"Reference 'today' (max release_date in data): {reference_today.date()}")

# review_score == 0 means "too few reviews to compute a score", not "bad" --
# treat as missing FOR AVERAGING PURPOSES ONLY. The underlying review_score
# column itself is left untouched elsewhere.
df["review_score_for_avg"] = df["review_score"].replace(0, np.nan)
print("review_score == 0 replaced with NaN in a separate averaging column (original review_score untouched).")

# rows with no primary_publisher can't be aggregated -- report, don't guess
missing_pub = df["primary_publisher"].isna().sum()
print(f"Rows with missing primary_publisher (excluded from aggregation): {missing_pub} ({missing_pub/len(df)*100:.1f}%)")

# =============================================================================
# TASK 3: AGGREGATE TO PUBLISHER LEVEL
# =============================================================================
print("\n" + "=" * 70)
print("TASK 3: AGGREGATE TO PUBLISHER LEVEL")
print("=" * 70)

grouped = df.groupby("primary_publisher")
publisher_features = grouped.agg(
    game_count=("app_id", "count"),
    review_score=("review_score_for_avg", "mean"),
    avg_owners_mid=("owners_mid", "mean"),
    avg_language_count=("language_count", "mean"),
    avg_positive_review_ratio=("review_positive_ratio", "mean"),
    avg_active_users_rate=("active_users_rate", "mean"),
    recent_release_count=("is_recent", "sum"),
).reset_index()

publisher_features["recent_release_ratio"] = (
    publisher_features["recent_release_count"] / publisher_features["game_count"]
)
print(f"Aggregated to {len(publisher_features)} publishers, 8 features computed.")

# =============================================================================
# TASK 4: DROP PUBLISHERS WITH game_count < MIN_GAMES
# =============================================================================
print("\n" + "=" * 70)
print(f"TASK 4: FILTER (game_count >= {MIN_GAMES})")
print("=" * 70)
n_before = len(publisher_features)
publisher_features = publisher_features[publisher_features["game_count"] >= MIN_GAMES].copy()
n_after = len(publisher_features)
print(f"Publishers before filter: {n_before}")
print(f"Publishers after filter (game_count >= {MIN_GAMES}): {n_after}")

# =============================================================================
# TASK 5: NORMALIZATION
# =============================================================================
# Scope decision (stated per the prompt): normalization method per feature
# is chosen from that feature's own computed skew on THIS aggregated data,
# not assumed up front.
#   - avg_owners_mid, avg_language_count, game_count, recent_release_count:
#     count/count-derived aggregates. If |skew| > 2 -> log1p + min-max
#     (compresses a heavy right tail before scaling to [0,1]); otherwise
#     plain min-max.
#   - avg_active_users_rate: conceptually a 0-1 ratio, but NOT reliably
#     bounded in this data -- a handful of games have steamspy-bucket-
#     mismatched owners_mid producing rates so extreme that even log1p
#     doesn't tame them, which would crush every other publisher toward 0
#     after min-max. Percentile rank is used instead: it only depends on
#     relative order, so it's immune to how extreme an outlier is.
#   - review_score (0-9), avg_positive_review_ratio, recent_release_ratio:
#     left unnormalized -- already bounded and directly interpretable;
#     scaling them further would only obscure the original scale.
print("\n" + "=" * 70)
print("TASK 5: NORMALIZATION")
print("=" * 70)

SKEW_THRESHOLD = 2.0
log_minmax_candidates = ["avg_owners_mid", "avg_language_count", "game_count", "recent_release_count"]
rank_scaled = ["avg_active_users_rate"]

normalization_log = {}
for col in log_minmax_candidates:
    col_skew = publisher_features[col].skew()
    if abs(col_skew) > SKEW_THRESHOLD:
        transformed = np.log1p(publisher_features[col])
        method = "log1p + min-max"
    else:
        transformed = publisher_features[col]
        method = "min-max"
    col_min, col_max = transformed.min(), transformed.max()
    publisher_features[col + "_norm"] = (transformed - col_min) / (col_max - col_min)
    normalization_log[col] = (col_skew, method)
    print(f"  {col:24s} skew={col_skew:7.2f}  method={method}")

for col in rank_scaled:
    publisher_features[col + "_norm"] = publisher_features[col].rank(pct=True)
    normalization_log[col] = (None, "percentile rank")
    print(f"  {col:24s}              method=percentile rank (bounded/unreliable-outlier ratio)")

print("\nLeft unnormalized (already bounded/interpretable): review_score (0-9), "
      "avg_positive_review_ratio (0-1), recent_release_ratio (0-1)")

# =============================================================================
# TASK 6: EXECUTE AND VALIDATE
# =============================================================================
print("\n" + "=" * 70)
print("TASK 6: EXECUTE AND VALIDATE")
print("=" * 70)
print("shape:", publisher_features.shape)
print("one row per publisher (no duplicates):", publisher_features["primary_publisher"].duplicated().sum() == 0)
print("all publishers meet game_count >= MIN_GAMES:", (publisher_features["game_count"] >= MIN_GAMES).all())

inf_check = np.isinf(publisher_features.select_dtypes(include=[np.number])).sum()
inf_cols = inf_check[inf_check > 0]
print("columns with inf/-inf values:", inf_cols.to_dict() if len(inf_cols) else "none")

norm_cols = [c for c in publisher_features.columns if c.endswith("_norm")]
in_range = publisher_features[norm_cols].apply(lambda s: s.dropna().between(0, 1).all())
print("all *_norm columns fall within [0,1]:", in_range.all())

print("\nmissing % per column:")
missingness = (publisher_features.isna().mean() * 100).round(2)
print(missingness.to_string())

publisher_features.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={publisher_features.shape}")

# =============================================================================
# TASK 7: DELIVER (short summary)
# =============================================================================
print("\n" + "=" * 70)
print("TASK 7: SUMMARY")
print("=" * 70)
print(f"Publishers: {n_before} before filter -> {n_after} after game_count >= {MIN_GAMES} filter.")
print(f"Rows excluded upstream for missing primary_publisher: {missing_pub} ({missing_pub/len(df)*100:.1f}% of games).")
print("\nNormalization method per feature (skew computed on this aggregated data):")
for col, (skew_val, method) in normalization_log.items():
    skew_str = f"skew={skew_val:.2f}" if skew_val is not None else "outlier-driven, not skew-based"
    print(f"  {col:24s} -> {method:20s} ({skew_str})")
print("\nColumns with the most missingness:")
print(missingness[missingness > 0].sort_values(ascending=False).to_string() or "  none")
print("\nTop 10 publishers by review_score (min 10 games, 0s excluded from average):")
print(publisher_features.nlargest(10, "review_score")[["primary_publisher", "game_count", "review_score"]].to_string(index=False))




''' PART 2: EVALUATING PUBLISHER SCORES '''
'''
Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a weighted scoring and ranking layer on top of an existing publisher-level feature table. Prioritize transparency and easy adjustability of every weight/assumption over cleverness.
Context: Input is publisher_features.csv — one row per primary_publisher, already aggregated and normalized (contains raw features like review_score, avg_owners_mid, avg_language_count, avg_positive_review_ratio, avg_active_users_rate, recent_release_ratio, game_count, recent_release_count, plus their _norm counterparts where applicable). The next step is to combine these into 4 weighted dimension scores and one overall weighted score, then rank publishers by it.

Objective: Produce publisher_scores.csv — one row per publisher — containing the 4 dimension scores, the overall weighted score, and a rank. Do not touch publisher_features.csv itself.
Weighting scheme (as specified): Scale & Reach (35%) = 80% player count (reach) + 20% language count Quality (30%) = 50/50 split of review score and positive review ratio Engagement (20%) = no sub-weights specified Growth & Momentum (15%) = 60% ratio + 40% games count
Scope decisions to make explicit up front (state each as a code comment, collected in one clearly-labeled, easily-editable place — not buried in calculation logic):
* "Player count" and "language count" map to avg_owners_mid_norm and avg_language_count_norm respectively (the already-normalized reach features from publisher_features.csv).
* Quality has  a 50/50 blend sub-split of review_score (0-9) and avg_positive_review_ratio (0-1, already bounded). Before, min-max scale the review_score to 0-1 (only for this blend — do not alter or re-save review_score itself elsewhere). Make the blend weights a named, editable variable.
* Engagement has only one available signal (avg_active_users_rate_norm) -- no sub-split needed.
* "Ratio" in Growth & Momentum maps to recent_release_ratio (already bounded 0-1, matches the name directly).
* "Games count" in Growth & Momentum is recent_release_count_norm (recent releases only). 

Tasks:
1. Load publisher_features.csv and report its shape.
2. Collect every weight (the 4 dimension weights, and the sub-weights within Scale & Reach, Quality, and Growth & Momentum) into named dictionaries/variables at the top of the script, each asserted to sum to 1.0. No weight value should appear inline inside a calculation.
3. Min-max scale review_score (0-9) to 0-1 in a new column, since it must be combined with avg_positive_review_ratio (already 0-1) into the Quality dimension — document that publisher_features.csv intentionally left review_score unnormalized, and this rescale exists only for this combination step.
4. Compute the 4 dimension scores using the weighted sums defined above.
5. Compute overall_score as the weighted sum of the 4 dimension scores using the top-level weights. If any dimension score is NaN for a publisher, overall_score must also be NaN for that publisher (no silent reweighting or fabrication) — report these publishers separately rather than dropping them.
6. Rank publishers by overall_score (descending; ties get the same rank, e.g. via "min" ranking method). Sort the output by rank.
7. Execute and validate:
    * Actually run the code.
    * Confirm: all 4 dimension scores and overall_score fall within [0,1] (where non-NaN), no duplicate publishers, and report how many publishers have a NaN overall_score and why.
8. Deliver:
    * The code, plus a short summary: top 10-15 publishers by overall_score with their dimension breakdown.

Constraints (Do Not):
* Do not hardcode any weight inline in a formula — every weight must be a named variable/dict entry, changeable in one place.
* Do not silently reweight or impute a dimension score to cover a missing input — propagate NaN and report it instead.
* Do not drop any publisher row, including those that end up with a NaN overall_score.
* Do not alter or re-save publisher_features.csv.
* Do not pick a resolution for either ambiguous mapping (Quality sub-split, "games count") without stating it explicitly as an assumption in both a code comment and the delivered summary.
* Do not overengineer — no additional dimensions, no speculative features, no scaling beyond what's needed to combine review_score with avg_positive_review_ratio.

Expected Output:
* publisher_scores.csv: one row per publisher, containing rank, primary_publisher, game_count, the 4 dimension scores (scale_reach_score, quality_score, engagement_score, momentum_score), and overall_score.
* A short written summary covering: the top-ranked publishers with their dimension breakdown, and the two stated assumptions for review/override.

Validation:
* Reload the output and confirm: no duplicate publishers, all dimension scores and overall_score fall within [0,1] where present, and the count of publishers with a NaN overall_score matches the count reported in the summary.

'''
# Request: 2026-08-20 20:15 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


"""
Score and rank publishers from publisher_features.csv using 4 weighted
dimensions. Structured to follow the task numbering in the source prompt
(Tasks 1-8) so each section below maps directly back to it.
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "data/feature_analysis/publisher_features.csv"
OUT = "data/feature_analysis/publisher_scores.csv"

# =============================================================================
# TASK 1: LOAD
# =============================================================================
df = pd.read_csv(SRC, low_memory=False)
print("=" * 70)
print("TASK 1: LOAD")
print("=" * 70)
print("Loaded publisher_features.csv:", df.shape)

# =============================================================================
# TASK 2: WEIGHTS -- every weight named, editable in one place, sums to 1
# =============================================================================
# Scope decisions (stated explicitly, per the prompt):
#   - "Player count" / "language count" -> avg_owners_mid_norm /
#     avg_language_count_norm (already-normalized reach features).
#   - Quality has no stated sub-split. Resolved as a 50/50 blend of
#     review_score (min-max'd to 0-1 in TASK 3) and avg_positive_review_ratio
#     (already 0-1).
#   - Engagement has only one signal (avg_active_users_rate_norm) -- no
#     sub-split needed.
#   - "Ratio" in Growth & Momentum -> recent_release_ratio (already 0-1,
#     matches the name directly).
#   - "Games count" in Growth & Momentum -> recent_release_count_norm
#     (recent releases only, NOT total portfolio size / game_count_norm).
print("\n" + "=" * 70)
print("TASK 2: WEIGHTS")
print("=" * 70)

DIMENSION_WEIGHTS = {
    "scale_reach_score": 0.35,
    "quality_score": 0.30,
    "engagement_score": 0.20,
    "momentum_score": 0.15,
}
assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-9, "dimension weights must sum to 1"

SCALE_REACH_WEIGHTS = {"avg_owners_mid_norm": 0.80, "avg_language_count_norm": 0.20}
assert abs(sum(SCALE_REACH_WEIGHTS.values()) - 1.0) < 1e-9, "scale & reach sub-weights must sum to 1"

QUALITY_WEIGHTS = {"review_score_norm": 0.50, "avg_positive_review_ratio": 0.50}
assert abs(sum(QUALITY_WEIGHTS.values()) - 1.0) < 1e-9, "quality sub-weights must sum to 1"

MOMENTUM_WEIGHTS = {"recent_release_ratio": 0.60, "recent_release_count_norm": 0.40}
assert abs(sum(MOMENTUM_WEIGHTS.values()) - 1.0) < 1e-9, "momentum sub-weights must sum to 1"

print("DIMENSION_WEIGHTS:", DIMENSION_WEIGHTS)
print("SCALE_REACH_WEIGHTS:", SCALE_REACH_WEIGHTS)
print("QUALITY_WEIGHTS:", QUALITY_WEIGHTS)
print("MOMENTUM_WEIGHTS:", MOMENTUM_WEIGHTS)

# =============================================================================
# TASK 3: RESCALE review_score FOR THE QUALITY BLEND ONLY
# =============================================================================
# publisher_features.csv intentionally left review_score (0-9) unnormalized
# to stay human-interpretable there. It's rescaled here, in a NEW column,
# only because this script needs to combine it with avg_positive_review_ratio
# (already 0-1) into a single Quality dimension. review_score itself is
# untouched and not re-saved.
print("\n" + "=" * 70)
print("TASK 3: RESCALE review_score (0-9 -> 0-1) FOR QUALITY BLEND")
print("=" * 70)
rs_min, rs_max = df["review_score"].min(), df["review_score"].max()
df["review_score_norm"] = (df["review_score"] - rs_min) / (rs_max - rs_min)
print(f"review_score range: [{rs_min}, {rs_max}] -> review_score_norm range: [0, 1]")

# =============================================================================
# TASK 4: DIMENSION SCORES
# =============================================================================
print("\n" + "=" * 70)
print("TASK 4: DIMENSION SCORES")
print("=" * 70)
df["scale_reach_score"] = sum(df[c] * w for c, w in SCALE_REACH_WEIGHTS.items())
df["quality_score"] = sum(df[c] * w for c, w in QUALITY_WEIGHTS.items())
df["engagement_score"] = df["avg_active_users_rate_norm"]
df["momentum_score"] = sum(df[c] * w for c, w in MOMENTUM_WEIGHTS.items())
print("Computed: scale_reach_score, quality_score, engagement_score, momentum_score")

# =============================================================================
# TASK 5: OVERALL SCORE -- NaN in any dimension propagates, never reweighted
# =============================================================================
print("\n" + "=" * 70)
print("TASK 5: OVERALL SCORE")
print("=" * 70)
DIMS = ["scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
df["overall_score"] = sum(df[c] * DIMENSION_WEIGHTS[c] for c in DIMS)

nan_overall = df["overall_score"].isna()
print(f"Publishers with NaN overall_score: {nan_overall.sum()}")
if nan_overall.sum() > 0:
    nan_reasons = df.loc[nan_overall, DIMS].isna()
    print("Which dimension(s) caused it (count of publishers missing each):")
    print(nan_reasons.sum().to_string())

# =============================================================================
# TASK 6: RANK
# =============================================================================
print("\n" + "=" * 70)
print("TASK 6: RANK")
print("=" * 70)
df["rank"] = df["overall_score"].rank(ascending=False, method="min").astype("Int64")
df = df.sort_values("overall_score", ascending=False, na_position="last")
print("Ranked by overall_score, descending, ties share the same rank (method='min').")

# =============================================================================
# TASK 7: EXECUTE AND VALIDATE
# =============================================================================
print("\n" + "=" * 70)
print("TASK 7: EXECUTE AND VALIDATE")
print("=" * 70)
for c in DIMS + ["overall_score"]:
    vals = df[c].dropna()
    in_range = vals.between(0, 1).all()
    print(f"  {c:20s} min={vals.min():.3f}  max={vals.max():.3f}  within [0,1]: {in_range}  NaN count={df[c].isna().sum()}")

dup_count = df["primary_publisher"].duplicated().sum()
print(f"\nduplicate publishers: {dup_count}")
print(f"NaN overall_score count matches TASK 5 report: {df['overall_score'].isna().sum() == nan_overall.sum()}")

# =============================================================================
# SAVE
# =============================================================================
final_cols = ["rank", "primary_publisher", "game_count"] + DIMS + ["overall_score"]
df[final_cols].to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={df[final_cols].shape}")

# =============================================================================
# TASK 8: DELIVER (short summary)
# =============================================================================
print("\n" + "=" * 70)
print("TASK 8: SUMMARY")
print("=" * 70)
print("Top 15 publishers by overall_score:")
print(df[final_cols].head(15).to_string(index=False))

print("\nAssumptions applied (stated for review/override):")
print("  1. Quality (30%) = 50/50 blend of review_score_norm and avg_positive_review_ratio")
print("     (no sub-split was specified; review_score min-max'd to 0-1 only for this blend).")
print("  2. Growth & Momentum 'games count' (40% of the 15% dimension) = "
      "recent_release_count_norm (recent releases only, not total portfolio size).")




''' PART 3: DOING THE SENSITIVITY ANALYSIS '''
'''# Publisher Scoring Sensitivity Analysis

## Role

You are a senior Data Analyst and Python/Pandas expert specializing in scoring models, sensitivity analysis, ranking stability, and data visualization.

Your task is to build and execute a **sensitivity analysis for an existing publisher scoring model**.

The purpose is **not** to find a better weighting scheme or optimize the model.

The purpose is to determine:

> **How robust are the publisher scores and rankings to reasonable changes in the four top-level dimension weights?**

The existing feature engineering and scoring methodology are already defined and must be treated as the baseline model.

Prioritize:

- methodological correctness
- transparency
- reproducibility
- ranking stability
- interpretable results
- clear visualizations

Do not overengineer the analysis.

---

# 1. Project Structure

The project has the following structure:

```text
project/
│
├── data/
│   └── feature_analysis/
│       ├── publisher_features.csv
│       ├── publisher_scores.csv
│       └── new_csv.csv
│
└── src/
    └── feature_engineering/
        ├── build_publisher_scores.py
        ├── new_file.py
        └── sensitivity_analysis.py

```

The new sensitivity-analysis script should be located in:

```text
src/feature_engineering/

```

Use:

```text
../../data/feature_analysis/publisher_features.csv

```

as the primary input.

Write all sensitivity-analysis outputs to:

```text
../../data/feature_analysis/

```

Do not modify:

```text
publisher_features.csv
publisher_scores.csv

```

The existing `publisher_scores.csv` should be used as a **baseline validation/reference file**, not as the primary input.

---

# 2. Important Principle

The existing pipeline has two distinct stages:

1. `publisher_features.csv`
   - publisher-level aggregated features
   - normalized features
   - produced by the existing feature-engineering process
2. `publisher_scores.csv`
   - four dimension scores
   - overall score
   - publisher ranking
   - produced by the existing scoring model

The sensitivity analysis sits **after the feature-engineering stage**.

Therefore:

### Do not redo feature engineering.

Do not:

- reaggregate game-level data
- change publisher filtering
- change normalization
- change the recent-release definition
- change the handling of missing values
- change the feature definitions

The sensitivity analysis must use the existing `publisher_features.csv` exactly as produced.

---

# 3. Existing Scoring Model

The existing scoring model contains four dimensions.

The baseline top-level weights are:

| DimensionBaseline weight |          |
| ------------------------ | -------- |
| Scale & Reach            | 35%      |
| Quality                  | 30%      |
| Engagement               | 20%      |
| Growth & Momentum        | 15%      |
| **Total**                | **100%** |

These four top-level weights are the **only weights that may change during the sensitivity analysis**.

---

# 4. Fixed Dimension Calculations

The internal construction of each dimension is part of the existing model and must remain completely unchanged.

## 4.1 Scale & Reach

Scale & Reach consists of:

```text
avg_owners_mid_norm       = 80%
avg_language_count_norm   = 20%

```

Calculate:

```text
scale_reach_score =
    0.80 * avg_owners_mid_norm
  + 0.20 * avg_language_count_norm

```

These sub-weights must remain fixed in every sensitivity scenario.

---

## 4.2 Quality

Quality consists of:

```text
review_score_norm             = 50%
avg_positive_review_ratio     = 50%

```

The existing scoring model creates `review_score_norm` by min-max scaling `review_score` within the scoring step:

```text
(review_score - minimum review_score)
/
(maximum review_score - minimum review_score)

```

This normalization is performed only for the scoring calculation.

Do not modify the original `review_score` column in `publisher_features.csv`.

Calculate:

```text
quality_score =
    0.50 * review_score_norm
  + 0.50 * avg_positive_review_ratio

```

These sub-weights must remain fixed in every sensitivity scenario.

---

## 4.3 Engagement

Engagement contains one signal:

```text
avg_active_users_rate_norm = 100%

```

Therefore:

```text
engagement_score =
    avg_active_users_rate_norm

```

No internal weight may be changed.

---

## 4.4 Growth & Momentum

Growth & Momentum consists of:

```text
recent_release_ratio       = 60%
recent_release_count_norm  = 40%

```

Calculate:

```text
momentum_score =
    0.60 * recent_release_ratio
  + 0.40 * recent_release_count_norm

```

These sub-weights must remain fixed.

---

# 5. Critical Scope Rule

The following must remain **identical across every scenario**:

- `publisher_features.csv`
- publisher population
- publisher filtering
- feature definitions
- normalization
- `review_score_norm` calculation
- Scale & Reach sub-weights
- Quality sub-weights
- Engagement calculation
- Growth & Momentum sub-weights
- missing-value treatment

Only these four values may change:

```text
Scale & Reach top-level weight
Quality top-level weight
Engagement top-level weight
Growth & Momentum top-level weight

```

Every scenario must satisfy:

```text
scale_reach_weight
+ quality_weight
+ engagement_weight
+ momentum_weight
= 1.0

```

Never create or evaluate an invalid scenario.

---

# 6. Baseline Reconstruction

Load:

```text
../../data/feature_analysis/publisher_features.csv

```

Then reconstruct the existing four dimension scores exactly according to Sections 4.1–4.4.

Calculate the baseline overall score:

```text
overall_score =
    0.35 * scale_reach_score
  + 0.30 * quality_score
  + 0.20 * engagement_score
  + 0.15 * momentum_score

```

Create the baseline ranking using the same ranking methodology as the existing scoring script:

```python
rank(method="min", ascending=False)

```

Do not silently change the ranking methodology.

---

# 7. Baseline Validation Against publisher\_scores.csv

If:

```text
../../data/feature_analysis/publisher_scores.csv

```

exists, use it to validate the reconstructed baseline.

Compare:

- publisher
- Scale & Reach score
- Quality score
- Engagement score
- Growth & Momentum score
- overall score
- rank

Use a reasonable floating-point tolerance when comparing numerical scores.

The validation should explicitly report:

- whether publisher populations match
- whether dimension scores match
- whether overall scores match
- whether rankings match
- which publishers differ, if any
- the maximum numerical difference

If discrepancies occur:

1. investigate them
2. report them clearly
3. do not silently ignore them

The sensitivity analysis must not proceed under the assumption that the reconstruction is correct without checking.

---

# 8. Scenario Generation

## 8.1 Objective

Generate a **systematic and reproducible sensitivity grid** around the baseline.

The baseline is:

```text
35% / 30% / 20% / 15%

```

Use a **5-percentage-point grid**.

The plausible sensitivity ranges are:

| DimensionMinimumBaselineMaximum |     |     |     |
| ------------------------------- | --- | --- | --- |
| Scale & Reach                   | 25% | 35% | 45% |
| Quality                         | 20% | 30% | 40% |
| Engagement                      | 10% | 20% | 30% |
| Growth & Momentum               | 5%  | 15% | 25% |

Each dimension may therefore take values in increments of 5 percentage points within its respective range.

For example:

```text
Scale & Reach:
25%, 30%, 35%, 40%, 45%

Quality:
20%, 25%, 30%, 35%, 40%

Engagement:
10%, 15%, 20%, 25%, 30%

Growth & Momentum:
5%, 10%, 15%, 20%, 25%

```

---

# 9. Valid Scenario Constraint

Generate all combinations within the ranges above.

Then retain **only combinations whose four weights sum to exactly 100%**.

For example:

```text
35 / 30 / 20 / 15

```

is valid because:

```text
35 + 30 + 20 + 15 = 100

```

A combination such as:

```text
45 / 40 / 30 / 25

```

must not be included because:

```text
45 + 40 + 30 + 25 = 140

```

Do not manually select scenarios.

The scenario-generation logic must be programmatic.

The baseline must occur **exactly once**.

Report:

```text
total candidate combinations
number of valid scenarios
number of invalid combinations removed

```

This makes the sensitivity analysis reproducible and transparent.

---

# 10. Scenario IDs

Give every valid scenario a unique identifier.

For example:

```text
S000
S001
S002
...

```

Use:

```text
S000

```

for the baseline scenario.

Also store the four weights with every scenario.

---

# 11. Scenario Calculation

For every valid scenario:

1. Keep the four dimension scores fixed.
2. Apply the scenario's four top-level weights.
3. Calculate the scenario overall score.
4. Rank all publishers.
5. Store the ranking.
6. Store the scenario weights.

The dimension scores must **not** be recalculated differently for different scenarios.

Only the top-level weighting changes.

Conceptually:

```text
scenario_score =
    w_scale * scale_reach_score
  + w_quality * quality_score
  + w_engagement * engagement_score
  + w_momentum * momentum_score

```

---

# 12. Missing Values

Preserve the existing model's missing-value behavior.

Do not:

- replace missing values with zero
- silently reweight the remaining dimensions
- fabricate scores
- drop publishers because of missing dimension scores

If any dimension score is missing for a publisher, the resulting overall score should remain missing.

Maintain the same publisher population across scenarios.

Report publishers with missing overall scores separately.

---

# 13. Ranking Methodology

Use the same ranking methodology as the existing scoring script:

```python
rank(method="min", ascending=False)

```

Ties must therefore receive the same rank.

Keep the ranking methodology consistent across all scenarios.

---

# 14. Ranking Stability Analysis

Ranking stability is the primary focus of the sensitivity analysis.

Calculate the following.

## 14.1 Rank Change

For each publisher and scenario:

```text
rank_change =
    scenario_rank - baseline_rank

```

Also calculate:

```text
absolute_rank_change =
    abs(rank_change)

```

Interpretation:

- negative = publisher moved upward
- positive = publisher moved downward
- zero = unchanged

---

# 15. Mean Absolute Rank Change

For every scenario calculate:

```text
mean_absolute_rank_change

```

This is:

```text
mean(abs(scenario_rank - baseline_rank))

```

It provides a simple overall measure of how much the scenario changes the ranking.

---

# 16. Spearman Rank Correlation

For every scenario calculate the Spearman rank correlation between:

```text
baseline ranking

```

and

```text
scenario ranking

```

Use the publisher population for which rankings are available.

Interpretation:

- close to 1 → rankings are very similar
- lower values → rankings differ more substantially

The baseline scenario should have:

```text
Spearman correlation = 1.0

```

apart from numerical issues.

---

# 17. Top-N Stability

Analyze:

- Top 5
- Top 10
- Top 20

For every publisher calculate:

```text
top_5_frequency
top_10_frequency
top_20_frequency

```

For example:

```text
top_10_frequency =
    number of scenarios in Top 10
    /
    total number of valid scenarios

```

Also calculate the **baseline Top-N retention**:

For each scenario:

```text
top_10_overlap =
    size of intersection(
        baseline Top 10,
        scenario Top 10
    )
    / 10

```

Do this for Top 5, Top 10, and Top 20.

This is important because a ranking can have a high overall Spearman correlation while still changing materially at the very top.

---

# 18. Publisher-Level Sensitivity

For every publisher calculate:

```text
primary_publisher
baseline_score
baseline_rank
min_score
max_score
mean_score
score_range
score_std
min_rank
max_rank
rank_range
mean_absolute_rank_change
top_5_frequency
top_10_frequency
top_20_frequency

```

Where:

```text
score_range = max_score - min_score
rank_range = max_rank - min_rank

```

This allows identification of:

### Stable publishers

Publishers with:

- small rank range
- small score range
- high Top-N frequency

### Sensitive publishers

Publishers with:

- large rank range
- large score range
- large mean absolute rank change
- low Top-N stability

Do not label publishers "stable" or "sensitive" based on arbitrary thresholds unless those thresholds are explicitly defined and justified.

---

# 19. Scenario-Level Summary

Create one row per scenario containing at least:

```text
scenario_id
scale_reach_weight
quality_weight
engagement_weight
momentum_weight
mean_absolute_rank_change
spearman_correlation
top_5_overlap
top_10_overlap
top_20_overlap

```

Also calculate:

```text
weight_distance_from_baseline

```

Define this explicitly.

Use the Euclidean distance between the scenario weight vector and the baseline weight vector:

```text
sqrt(
    (w_scale - 0.35)^2
  + (w_quality - 0.30)^2
  + (w_engagement - 0.20)^2
  + (w_momentum - 0.15)^2
)

```

This gives a systematic measure of how far a scenario is from the baseline assumptions.

---

# 20. Dimension-Level Sensitivity

In addition to the complete scenario grid, determine which dimension appears to have the greatest influence on ranking changes.

Use the existing valid scenarios to evaluate this rather than changing internal sub-weights.

Analyze the relationship between each dimension's top-level weight and:

```text
mean_absolute_rank_change

```

and:

```text
Spearman correlation

```

For example, examine whether higher:

```text
Scale & Reach weight

```

is systematically associated with larger or smaller ranking changes.

Repeat for:

- Scale & Reach
- Quality
- Engagement
- Growth & Momentum

Do not claim causality merely from correlation.

Describe this as an indication of which dimension's weighting is associated with greater ranking sensitivity.

---

# 21. Controlled Dimension Tests

In addition to the full grid, create a small set of interpretable representative scenarios.

Use the following logic:

### Baseline

```text
35 / 30 / 20 / 15

```

### Scale & Reach emphasis

Increase Scale & Reach by 10 percentage points relative to baseline while redistributing the required 10 percentage points across the other dimensions in a clearly defined and reproducible way.

### Quality emphasis

Increase Quality by 10 percentage points.

### Engagement emphasis

Increase Engagement by 10 percentage points.

### Growth & Momentum emphasis

Increase Growth & Momentum by 10 percentage points.

The redistribution rule must be defined **before examining results**.

Prefer a proportional redistribution of the other three baseline weights so that:

```text
all four weights remain non-negative
sum = 100%

```

Document the rule in the code.

These representative scenarios are for interpretation only; the full 5-point grid remains the main sensitivity analysis.

---

# 22. Visualizations

Create clear and readable visualizations using:

- pandas
- numpy
- matplotlib
- seaborn
- scipy where appropriate

Do not create unnecessary plots.

Save all plots to:

```text
../../data/feature_analysis/sensitivity_plots/

```

Do not overwrite unrelated existing files.

---

# 23. Required Plot 1 — Scenario Weight Distribution

Show the distribution of tested weights for:

- Scale & Reach
- Quality
- Engagement
- Growth & Momentum

The purpose is to make the tested sensitivity range immediately understandable.

Clearly indicate the baseline values.

---

# 24. Required Plot 2 — Ranking Stability

Show the distribution of:

```text
absolute rank change

```

across publishers and scenarios.

A boxplot is appropriate.

The plot should communicate how much publisher rankings typically move under alternative weighting assumptions.

---

# 25. Required Plot 3 — Scenario Similarity to Baseline

Create a scatter plot:

```text
x = weight_distance_from_baseline
y = Spearman correlation with baseline

```

Each point represents a scenario.

Highlight the baseline scenario.

This shows whether increasingly different weighting assumptions actually result in increasingly different rankings.

---

# 26. Required Plot 4 — Top-N Stability

Visualize Top-N stability across scenarios.

At minimum show:

- Top 5 overlap
- Top 10 overlap
- Top 20 overlap

Use an appropriate line or distribution plot.

The goal is to answer:

> How much of the baseline Top 5/10/20 remains under alternative weighting assumptions?

---

# 27. Required Plot 5 — Publisher Top-10 Frequency

Show the publishers that appear in the Top 10 most frequently.

Focus on publishers with meaningful Top-10 frequency.

Sort from most stable to least stable.

Do not create an unreadable plot containing every publisher.

---

# 28. Required Plot 6 — Publisher Score Sensitivity

For selected important publishers, show:

```text
minimum score
baseline score
maximum score

```

Use an error-bar/range visualization.

Select publishers using a predefined rule such as:

- baseline Top 10

rather than selecting publishers after examining the results.

---

# 29. Required Plot 7 — Rank Sensitivity Heatmap

Create a heatmap showing publisher ranks across representative scenarios.

Use the baseline Top 10 or Top 20 publishers.

The purpose is to visually show which highly ranked publishers are stable and which move substantially.

---

# 30. Required Plot 8 — Dimension Weight vs Ranking Sensitivity

Create an appropriate visualization showing the relationship between each dimension's weight and:

```text
mean_absolute_rank_change

```

This should help identify which dimension's weighting is most strongly associated with ranking changes.

Clearly state that this is an association within the tested scenario grid, not a causal estimate.

---

# 31. Representative Scenario Reporting

For the baseline and the four dimension-emphasis scenarios, report:

```text
scenario_id
weights
mean_absolute_rank_change
Spearman correlation
Top 5 overlap
Top 10 overlap
Top 20 overlap
Top 10 publishers

```

Also report how each Top-10 publisher's rank differs from the baseline.

---

# 32. Validation

Perform explicit validation before considering the analysis complete.

## Input validation

Confirm:

- `publisher_features.csv` loads successfully
- expected columns exist
- publisher count is correct
- no duplicate publishers
- no unexpected infinite values

---

## Dimension validation

Confirm:

- Scale & Reach scores are within [0,1]
- Quality scores are within [0,1]
- Engagement scores are within [0,1]
- Growth & Momentum scores are within [0,1]

where values are non-NaN.

---

## Scenario validation

Confirm:

- every scenario contains exactly four weights
- every weight is within its predefined range
- every scenario sums to exactly 1.0
- baseline exists exactly once
- scenario IDs are unique
- there are no duplicate weight combinations

---

## Result validation

Confirm:

- no duplicate publisher/scenario combinations
- scenario score values are within [0,1] where non-NaN
- rankings are correctly ordered
- ties are handled consistently
- no unexpected infinite values exist
- publisher count remains consistent across scenarios

---

## Completeness validation

Confirm:

```text
number of valid scenarios
×
number of publishers

```

matches the expected number of scenario-level observations, subject to the documented missing-value handling.

---

# 33. Output Files

Write the following files to:

```text
../../data/feature_analysis/

```

## 33.1 Scenario-Level Results

Create:

```text
publisher_sensitivity_results.csv

```

Columns:

```text
scenario_id
scale_reach_weight
quality_weight
engagement_weight
momentum_weight
weight_distance_from_baseline
primary_publisher
overall_score
rank
baseline_rank
rank_change
absolute_rank_change

```

---

## 33.2 Publisher Sensitivity Summary

Create:

```text
publisher_sensitivity_summary.csv

```

Columns:

```text
primary_publisher
baseline_score
baseline_rank
min_score
max_score
mean_score
score_range
score_std
min_rank
max_rank
rank_range
mean_absolute_rank_change
top_5_frequency
top_10_frequency
top_20_frequency

```

---

## 33.3 Scenario Summary

Create:

```text
scenario_sensitivity_summary.csv

```

Columns:

```text
scenario_id
scale_reach_weight
quality_weight
engagement_weight
momentum_weight
weight_distance_from_baseline
mean_absolute_rank_change
spearman_correlation
top_5_overlap
top_10_overlap
top_20_overlap

```

---

## 33.4 Dimension Sensitivity Summary

Create:

```text
dimension_sensitivity_summary.csv

```

For each dimension report statistics such as:

```text
dimension
correlation_weight_vs_mean_abs_rank_change
correlation_weight_vs_spearman
min_weight
max_weight
baseline_weight

```

Clearly document the interpretation of these statistics.

---

# 34. Code Structure

Create one executable Python script:

```text
src/feature_engineering/sensitivity_analysis.py

```

Structure it into clear sections:

```text
1. Configuration
2. Load publisher_features.csv
3. Validate input
4. Reconstruct fixed dimension scores
5. Validate baseline against publisher_scores.csv
6. Generate 5-point sensitivity grid
7. Validate scenarios
8. Calculate scenario scores
9. Calculate rankings
10. Calculate ranking stability
11. Calculate Top-N stability
12. Calculate publisher sensitivity
13. Calculate dimension-level sensitivity
14. Generate representative scenarios
15. Generate visualizations
16. Save CSV outputs
17. Final validation
18. Print final summary

```

Keep all important assumptions in one clearly visible configuration section at the top.

For example:

```python
INPUT_PATH
OUTPUT_DIR
BASELINE_WEIGHTS
SENSITIVITY_RANGES
GRID_STEP
TOP_N_VALUES

```

Do not bury important assumptions inside calculation logic.

---

# 35. Reproducibility

The analysis must be completely reproducible.

Do not:

- manually select scenarios after seeing results
- manually select publishers because they look interesting
- optimize the weighting scheme
- alter the baseline model
- introduce arbitrary thresholds without documentation

The same input files and code should produce the same scenario set and results.

---

# 36. Interpretation Principles

The analysis must distinguish between four concepts.

## Score sensitivity

How much do numerical publisher scores change?

## Ranking sensitivity

How much do publisher positions change?

## Top-N sensitivity

How stable are the Top 5, Top 10, and Top 20?

## Dimension sensitivity

Which dimension's top-level weight is most strongly associated with ranking changes?

Do not treat these as interchangeable.

A model can have:

- relatively large score changes
- but very stable rankings

or:

- small score changes
- but meaningful ranking changes when publishers are close together.

Interpret these separately.

---

# 37. Important Statistical Interpretation

Do not conclude that a weighting dimension **causes** ranking instability merely because its weight correlates with rank changes.

The scenario grid changes several weights simultaneously because they must sum to 100%.

Therefore, dimension-level results should be described as:

> "associated with ranking sensitivity within the tested scenario space"

rather than:

> "causes ranking sensitivity."

---

# 38. Final Analysis

After executing the analysis, provide a concise but evidence-based report.

## Dataset

Report:

- number of publishers
- number of candidate weight combinations
- number of valid scenarios
- number of invalid combinations removed

---

## Baseline

Report:

- baseline weights
- baseline Top 10
- baseline score distribution
- validation against `publisher_scores.csv`

---

## Overall Ranking Stability

Report:

- mean absolute rank change across scenarios
- minimum and maximum Spearman correlation
- median Spearman correlation
- largest observed rank movements

---

## Top-N Robustness

Report:

- Top 5 overlap statistics
- Top 10 overlap statistics
- Top 20 overlap statistics

Explain whether the most highly ranked publishers remain stable.

---

## Most Stable Publishers

Identify publishers based on:

- small rank range
- small score range
- high Top-10 frequency

---

## Most Sensitive Publishers

Identify publishers based on:

- large rank range
- large score range
- large mean absolute rank change
- low Top-N frequency

---

## Dimension Sensitivity

Identify which dimension's weighting is most strongly associated with ranking changes within the tested scenario grid.

Support this with the calculated statistics.

---

# 39. Final Conclusion

Explicitly answer:

> **Is the baseline 35% Scale & Reach / 30% Quality / 20% Engagement / 15% Growth & Momentum weighting reasonably robust to plausible alternative top-level weightings?**

The answer must be based on quantitative evidence from:

- rank changes
- Spearman correlations
- Top-N overlap
- publisher-level sensitivity
- scenario distance from baseline

Do not simply state:

> "The model is robust."

Instead explain **why** the evidence supports or does not support that conclusion.

If the results show mixed evidence, explicitly say so.

For example, distinguish between:

- robust overall ranking
- unstable individual publishers
- stable Top 5 but less stable Top 20
- stable rankings despite noticeable score changes

---

# 40. Final Deliverable

Return:

1. The complete executable Python code.
2. The scenario-generation methodology.
3. The exact number of valid scenarios generated.
4. Validation results.
5. The generated CSV outputs.
6. The generated plots.
7. A concise interpretation of the sensitivity results.
8. The most stable publishers.
9. The most sensitive publishers.
10. Dimension-level sensitivity results.
11. Top-N robustness results.
12. A final evidence-based assessment of the robustness of the baseline 35/30/20/15 weighting.

The existing files must remain untouched:

```text
publisher_features.csv
publisher_scores.csv

```

Only the new sensitivity-analysis outputs should be created.'''

# Request: 2026-08-21 2 0:04 CET.
# Author: Christian Beemelmann (prompt and adjustments), ChatGPT (code)

"""
Sensitivity analysis for the existing publisher scoring model.

Run from this file's directory:
    python sensitivity_analysis.py

The script intentionally reconstructs the baseline from publisher_features.csv
and uses publisher_scores.csv only as a validation/reference file.
"""

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
from pathlib import Path
import itertools
import math
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, pearsonr

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Paths are relative to src/feature_engineering/, as requested.
INPUT_PATH = Path("../../data/feature_analysis/publisher_features.csv")
BASELINE_REFERENCE_PATH = Path("../../data/feature_analysis/publisher_scores.csv")
OUTPUT_DIR = Path("../../data/feature_analysis")
PLOT_DIR = OUTPUT_DIR / "sensitivity_plots"

BASELINE_WEIGHTS = {
    "scale_reach_weight": 0.35,
    "quality_weight": 0.30,
    "engagement_weight": 0.20,
    "momentum_weight": 0.15,
}

SENSITIVITY_RANGES = {
    "scale_reach_weight": (0.25, 0.45),
    "quality_weight": (0.20, 0.40),
    "engagement_weight": (0.10, 0.30),
    "momentum_weight": (0.05, 0.25),
}

GRID_STEP = 0.05
TOP_N_VALUES = (5, 10, 20)
BASELINE_SCENARIO_ID = "S000"

# Fixed internal dimension construction: these NEVER change in sensitivity scenarios.
SCALE_REACH_SUBWEIGHTS = {
    "avg_owners_mid_norm": 0.80,
    "avg_language_count_norm": 0.20,
}
QUALITY_SUBWEIGHTS = {
    "review_score_norm": 0.50,
    "avg_positive_review_ratio": 0.50,
}
MOMENTUM_SUBWEIGHTS = {
    "recent_release_ratio": 0.60,
    "recent_release_count_norm": 0.40,
}

REQUIRED_FEATURE_COLUMNS = [
    "primary_publisher",
    "game_count",
    "review_score",
    "avg_owners_mid_norm",
    "avg_language_count_norm",
    "avg_positive_review_ratio",
    "avg_active_users_rate_norm",
    "recent_release_ratio",
    "recent_release_count_norm",
]

RANK_COLUMNS = [
    "scale_reach_score",
    "quality_score",
    "engagement_score",
    "momentum_score",
    "overall_score",
    "rank",
]

# =============================================================================
# 2. HELPERS
# =============================================================================
def assert_close_series(a, b, tolerance=1e-9):
    """Return comparison statistics for two aligned numeric Series."""
    diff = (a.astype(float) - b.astype(float)).abs()
    max_diff = diff.max(skipna=True)
    mismatch = ~np.isclose(
        a.astype(float),
        b.astype(float),
        rtol=0.0,
        atol=tolerance,
        equal_nan=True,
    )
    return int(mismatch.sum()), float(max_diff) if pd.notna(max_diff) else 0.0


def validate_no_inf(dataframe, name):
    numeric = dataframe.select_dtypes(include=[np.number])
    inf_count = int(np.isinf(numeric.to_numpy()).sum())
    if inf_count:
        raise ValueError(f"{name} contains {inf_count} inf/-inf values.")


def minmax(series):
    minimum = series.min()
    maximum = series.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series(np.nan, index=series.index)
    return (series - minimum) / (maximum - minimum)


def weighted_dimension(df, weights):
    """Weighted sum with normal pandas NaN propagation."""
    result = pd.Series(0.0, index=df.index)
    valid = pd.Series(True, index=df.index)
    for column, weight in weights.items():
        valid &= df[column].notna()
        result += df[column] * weight
    return result.where(valid, np.nan)


def build_scenario_id(i):
    return f"S{i:03d}"


def generate_scenarios():
    names = list(BASELINE_WEIGHTS.keys())
    value_lists = []
    for name in names:
        low, high = SENSITIVITY_RANGES[name]
        values = np.arange(low, high + GRID_STEP / 2, GRID_STEP)
        values = np.round(values, 10)
        value_lists.append(values)

    candidates = list(itertools.product(*value_lists))
    valid = [combo for combo in candidates if np.isclose(sum(combo), 1.0, atol=1e-10)]

    rows = []
    for i, combo in enumerate(valid):
        row = dict(zip(names, combo))
        rows.append(row)

    scenarios = pd.DataFrame(rows)
    # Force the baseline to S000, while preserving deterministic ordering.
    baseline_mask = np.isclose(
        scenarios[names].to_numpy(),
        np.array([BASELINE_WEIGHTS[n] for n in names]),
        atol=1e-10,
    ).all(axis=1)

    if baseline_mask.sum() != 1:
        raise ValueError("Baseline scenario must occur exactly once.")

    baseline_row = scenarios.loc[baseline_mask].iloc[0]
    remaining = scenarios.loc[~baseline_mask].copy()

    # Sort deterministically by the four weights.
    remaining = remaining.sort_values(names, ascending=True).reset_index(drop=True)
    scenarios = pd.concat([baseline_row.to_frame().T, remaining], ignore_index=True)
    scenarios.insert(0, "scenario_id", [build_scenario_id(i) for i in range(len(scenarios))])

    return candidates, scenarios


def weight_distance(row):
    return float(
        np.sqrt(
            sum(
                (row[name] - BASELINE_WEIGHTS[name]) ** 2
                for name in BASELINE_WEIGHTS
            )
        )
    )


def proportional_emphasis_scenarios():
    """
    Increase one target dimension by +10 percentage points.

    Redistribution rule is defined before looking at results:
    the other three baseline weights are multiplied by a common factor
    so that they collectively absorb the 10 percentage-point reduction.
    """
    rows = [
        ("BASELINE", BASELINE_WEIGHTS.copy()),
    ]
    for target in BASELINE_WEIGHTS:
        weights = BASELINE_WEIGHTS.copy()
        target_new = weights[target] + 0.10
        other_total = 1.0 - weights[target]
        new_other_total = 1.0 - target_new
        factor = new_other_total / other_total

        for name in weights:
            if name != target:
                weights[name] *= factor
        weights[target] = target_new

        if not np.isclose(sum(weights.values()), 1.0):
            raise ValueError(f"Representative scenario {target} does not sum to 1.")
        rows.append((target.upper().replace("_WEIGHT", ""), weights))

    return rows


def rank_for_scores(scores):
    """Rank descending, ties get method='min', NaN remains NaN."""
    return scores.rank(method="min", ascending=False)


# =============================================================================
# 3. LOAD PUBLISHER FEATURES
# =============================================================================
print("=" * 80)
print("PUBLISHER SCORING SENSITIVITY ANALYSIS")
print("=" * 80)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_PATH.exists():
    raise FileNotFoundError(f"Missing input: {INPUT_PATH}")

features = pd.read_csv(INPUT_PATH, low_memory=False)
print(f"\nLoaded publisher_features.csv: {features.shape}")

missing_required = [c for c in REQUIRED_FEATURE_COLUMNS if c not in features.columns]
if missing_required:
    raise ValueError(f"Missing required feature columns: {missing_required}")

if features["primary_publisher"].duplicated().any():
    raise ValueError("publisher_features.csv contains duplicate publishers.")

validate_no_inf(features, "publisher_features.csv")

publisher_count = len(features)
print(f"Publisher count: {publisher_count}")
print(f"Duplicate publishers: {features['primary_publisher'].duplicated().sum()}")

# =============================================================================
# 4. INPUT VALIDATION
# =============================================================================
print("\nInput validation")
print("-" * 80)
print("Required columns present: True")
print(f"Unexpected duplicate publishers: {features['primary_publisher'].duplicated().sum()}")
print(f"Any inf/-inf values: {np.isinf(features.select_dtypes(include=[np.number]).to_numpy()).any()}")

missingness = (features.isna().mean() * 100).round(2)
if missingness.gt(0).any():
    print("Columns with missing values:")
    print(missingness[missingness > 0].sort_values(ascending=False).to_string())
else:
    print("Missing values: none")

# =============================================================================
# 5. RECONSTRUCT FIXED DIMENSION SCORES
# =============================================================================
print("\nReconstructing baseline dimension scores")
print("-" * 80)

# Exactly follows the existing scoring logic:
# review_score is min-max scaled only for the Quality blend.
features["review_score_norm"] = minmax(features["review_score"])

features["scale_reach_score"] = weighted_dimension(
    features, SCALE_REACH_SUBWEIGHTS
)
features["quality_score"] = weighted_dimension(
    features, QUALITY_SUBWEIGHTS
)
features["engagement_score"] = features["avg_active_users_rate_norm"]
features["momentum_score"] = weighted_dimension(
    features, MOMENTUM_SUBWEIGHTS
)

# Explicit NaN propagation: if any dimension is missing, overall_score is missing.
dimension_cols = [
    "scale_reach_score",
    "quality_score",
    "engagement_score",
    "momentum_score",
]
dimension_complete = features[dimension_cols].notna().all(axis=1)
features["overall_score"] = (
    features[dimension_cols]
    .mul(
        pd.Series(
            {
                "scale_reach_score": BASELINE_WEIGHTS["scale_reach_weight"],
                "quality_score": BASELINE_WEIGHTS["quality_weight"],
                "engagement_score": BASELINE_WEIGHTS["engagement_weight"],
                "momentum_score": BASELINE_WEIGHTS["momentum_weight"],
            }
        ),
        axis=1,
    )
    .sum(axis=1)
    .where(dimension_complete, np.nan)
)
features["rank"] = rank_for_scores(features["overall_score"])

# Validate dimensions.
print("Dimension ranges:")
for col in dimension_cols:
    vals = features[col].dropna()
    print(
        f"  {col:22s} [{vals.min():.6f}, {vals.max():.6f}] "
        f"within [0,1]={vals.between(0,1).all()}"
    )

# =============================================================================
# 6. BASELINE VALIDATION AGAINST publisher_scores.csv
# =============================================================================
print("\nBaseline validation against publisher_scores.csv")
print("-" * 80)

reference_exists = BASELINE_REFERENCE_PATH.exists()
validation = {
    "reference_exists": reference_exists,
    "publisher_population_match": None,
    "dimension_scores_match": {},
    "overall_score_match": None,
    "rank_match": None,
    "max_numerical_difference": 0.0,
    "mismatching_publishers": {},
}

if reference_exists:
    reference = pd.read_csv(BASELINE_REFERENCE_PATH, low_memory=False)
    print(f"Reference shape: {reference.shape}")

    left_publishers = set(features["primary_publisher"])
    right_publishers = set(reference["primary_publisher"])
    validation["publisher_population_match"] = left_publishers == right_publishers
    print(f"Publisher populations match: {validation['publisher_population_match']}")

    merged = features[
        ["primary_publisher", "scale_reach_score", "quality_score",
         "engagement_score", "momentum_score", "overall_score", "rank"]
    ].merge(
        reference[
            ["primary_publisher", "scale_reach_score", "quality_score",
             "engagement_score", "momentum_score", "overall_score", "rank"]
        ],
        on="primary_publisher",
        how="outer",
        suffixes=("_reconstructed", "_reference"),
        indicator=True,
    )

    if not (merged["_merge"] == "both").all():
        print("Warning: publisher population mismatch detected.")
    else:
        for col in dimension_cols + ["overall_score"]:
            recon = merged[f"{col}_reconstructed"]
            ref = merged[f"{col}_reference"]
            mismatch_count, max_diff = assert_close_series(recon, ref, tolerance=1e-9)
            validation["dimension_scores_match"][col] = mismatch_count == 0
            validation["max_numerical_difference"] = max(
                validation["max_numerical_difference"], max_diff
            )
            print(
                f"{col:22s} match={mismatch_count == 0} "
                f"mismatching_publishers={mismatch_count} max_abs_diff={max_diff:.12g}"
            )

            if mismatch_count:
                validation["mismatching_publishers"][col] = merged.loc[
                    ~np.isclose(recon, ref, rtol=0.0, atol=1e-9, equal_nan=True),
                    "primary_publisher",
                ].tolist()

        rank_recon = merged["rank_reconstructed"].astype(float)
        rank_ref = merged["rank_reference"].astype(float)
        rank_mismatch = ~np.isclose(
            rank_recon, rank_ref, rtol=0.0, atol=0.0, equal_nan=True
        )
        validation["rank_match"] = int(rank_mismatch.sum()) == 0
        print(
            f"{'rank':22s} match={validation['rank_match']} "
            f"mismatching_publishers={int(rank_mismatch.sum())}"
        )
        validation["overall_score_match"] = validation["dimension_scores_match"]["overall_score"]

        if validation["mismatching_publishers"].get("momentum_score"):
            print(
                "\nIMPORTANT VALIDATION FINDING: reconstructed Growth & Momentum "
                "does not match publisher_scores.csv."
            )
            print(
                "The supplied build_publisher_scores.py explicitly defines "
                "'recent_release_count_norm' for this component, but the supplied "
                "publisher_scores.csv is numerically consistent with "
                "'game_count_norm' instead. The sensitivity analysis therefore "
                "follows the methodology specified in this sensitivity prompt "
                "and treats publisher_scores.csv strictly as a reference/validation file."
            )
else:
    print("publisher_scores.csv not found; baseline reference validation skipped.")

# =============================================================================
# 7. GENERATE 5-POINT SENSITIVITY GRID
# =============================================================================
print("\nScenario generation")
print("-" * 80)

candidates, scenarios = generate_scenarios()
candidate_count = len(candidates)
valid_count = len(scenarios)
invalid_count = candidate_count - valid_count

print(f"Candidate combinations: {candidate_count}")
print(f"Valid scenarios: {valid_count}")
print(f"Invalid combinations removed: {invalid_count}")
print(f"Baseline occurrences: {(scenarios['scenario_id'] == BASELINE_SCENARIO_ID).sum()}")

# Validate ranges, sums, uniqueness.
for col, (low, high) in SENSITIVITY_RANGES.items():
    assert scenarios[col].between(low, high).all(), f"{col} outside range."
    # 5-point grid membership:
    steps = (scenarios[col] - low) / GRID_STEP
    assert np.isclose(steps, np.round(steps)).all(), f"{col} outside 5-point grid."

assert np.isclose(scenarios[list(BASELINE_WEIGHTS)].sum(axis=1), 1.0, atol=1e-10).all()
assert scenarios["scenario_id"].is_unique
assert not scenarios[list(BASELINE_WEIGHTS)].duplicated().any()

scenarios["weight_distance_from_baseline"] = scenarios.apply(weight_distance, axis=1)

# =============================================================================
# 8. CALCULATE SCENARIO SCORES AND RANKINGS
# =============================================================================
print("\nCalculating scenario scores and rankings")
print("-" * 80)

scenario_rows = []

for _, scenario in scenarios.iterrows():
    weights = {
        "scale_reach_score": scenario["scale_reach_weight"],
        "quality_score": scenario["quality_weight"],
        "engagement_score": scenario["engagement_weight"],
        "momentum_score": scenario["momentum_weight"],
    }

    complete = features[dimension_cols].notna().all(axis=1)
    scenario_score = (
        features[dimension_cols]
        .mul(pd.Series(weights), axis=1)
        .sum(axis=1)
        .where(complete, np.nan)
    )
    scenario_rank = rank_for_scores(scenario_score)

    tmp = pd.DataFrame(
        {
            "scenario_id": scenario["scenario_id"],
            "scale_reach_weight": scenario["scale_reach_weight"],
            "quality_weight": scenario["quality_weight"],
            "engagement_weight": scenario["engagement_weight"],
            "momentum_weight": scenario["momentum_weight"],
            "weight_distance_from_baseline": scenario["weight_distance_from_baseline"],
            "primary_publisher": features["primary_publisher"],
            "overall_score": scenario_score,
            "rank": scenario_rank,
        }
    )
    scenario_rows.append(tmp)

scenario_results = pd.concat(scenario_rows, ignore_index=True)

baseline_lookup = features.set_index("primary_publisher")
scenario_results["baseline_rank"] = scenario_results["primary_publisher"].map(
    baseline_lookup["rank"]
)
scenario_results["rank_change"] = (
    scenario_results["rank"] - scenario_results["baseline_rank"]
)
scenario_results["absolute_rank_change"] = scenario_results["rank_change"].abs()

# Exact required output column order.
scenario_results = scenario_results[
    [
        "scenario_id",
        "scale_reach_weight",
        "quality_weight",
        "engagement_weight",
        "momentum_weight",
        "weight_distance_from_baseline",
        "primary_publisher",
        "overall_score",
        "rank",
        "baseline_rank",
        "rank_change",
        "absolute_rank_change",
    ]
]

# =============================================================================
# 9. RANKING STABILITY AND TOP-N STABILITY
# =============================================================================
print("\nRanking stability")
print("-" * 80)

baseline_top = {}
for n in TOP_N_VALUES:
    baseline_top[n] = set(
        features.loc[features["rank"].notna()]
        .nsmallest(n, "rank")["primary_publisher"]
    )

scenario_summary_rows = []

for scenario_id, group in scenario_results.groupby("scenario_id", sort=False):
    available = group.dropna(subset=["rank", "baseline_rank"]).copy()

    mean_abs_rank_change = available["absolute_rank_change"].mean()

    if len(available) >= 2:
        rho = spearmanr(
            available["baseline_rank"].astype(float),
            available["rank"].astype(float),
        ).statistic
    else:
        rho = np.nan

    overlap = {}
    for n in TOP_N_VALUES:
        scenario_top = set(
            group.dropna(subset=["rank"])
            .nsmallest(n, "rank")["primary_publisher"]
        )
        overlap[n] = len(baseline_top[n].intersection(scenario_top)) / n

    srow = scenarios.loc[scenarios["scenario_id"] == scenario_id].iloc[0]
    scenario_summary_rows.append(
        {
            "scenario_id": scenario_id,
            "scale_reach_weight": srow["scale_reach_weight"],
            "quality_weight": srow["quality_weight"],
            "engagement_weight": srow["engagement_weight"],
            "momentum_weight": srow["momentum_weight"],
            "weight_distance_from_baseline": srow["weight_distance_from_baseline"],
            "mean_absolute_rank_change": mean_abs_rank_change,
            "spearman_correlation": rho,
            "top_5_overlap": overlap[5],
            "top_10_overlap": overlap[10],
            "top_20_overlap": overlap[20],
        }
    )

scenario_summary = pd.DataFrame(scenario_summary_rows)

# =============================================================================
# 10. PUBLISHER-LEVEL SENSITIVITY
# =============================================================================
print("\nPublisher-level sensitivity")
print("-" * 80)

valid_scenario_results = scenario_results.dropna(subset=["overall_score", "rank"]).copy()

publisher_summary = (
    valid_scenario_results.groupby("primary_publisher")
    .agg(
        min_score=("overall_score", "min"),
        max_score=("overall_score", "max"),
        mean_score=("overall_score", "mean"),
        score_std=("overall_score", "std"),
        min_rank=("rank", "min"),
        max_rank=("rank", "max"),
        mean_absolute_rank_change=("absolute_rank_change", "mean"),
    )
    .reset_index()
)

publisher_summary["score_range"] = (
    publisher_summary["max_score"] - publisher_summary["min_score"]
)
publisher_summary["rank_range"] = (
    publisher_summary["max_rank"] - publisher_summary["min_rank"]
)

baseline_info = features[
    ["primary_publisher", "overall_score", "rank"]
].rename(
    columns={"overall_score": "baseline_score", "rank": "baseline_rank"}
)
publisher_summary = baseline_info.merge(
    publisher_summary, on="primary_publisher", how="left"
)

for n in TOP_N_VALUES:
    freq = (
        valid_scenario_results.assign(
            in_top_n=valid_scenario_results["rank"] <= n
        )
        .groupby("primary_publisher")["in_top_n"]
        .mean()
        .rename(f"top_{n}_frequency")
    )
    publisher_summary = publisher_summary.merge(
        freq, on="primary_publisher", how="left"
    )

publisher_summary = publisher_summary[
    [
        "primary_publisher",
        "baseline_score",
        "baseline_rank",
        "min_score",
        "max_score",
        "mean_score",
        "score_range",
        "score_std",
        "min_rank",
        "max_rank",
        "rank_range",
        "mean_absolute_rank_change",
        "top_5_frequency",
        "top_10_frequency",
        "top_20_frequency",
    ]
].sort_values(["baseline_rank", "primary_publisher"])

# =============================================================================
# 11. DIMENSION-LEVEL SENSITIVITY
# =============================================================================
print("\nDimension-level sensitivity")
print("-" * 80)

dimension_map = {
    "Scale & Reach": "scale_reach_weight",
    "Quality": "quality_weight",
    "Engagement": "engagement_weight",
    "Growth & Momentum": "momentum_weight",
}

dimension_rows = []
for dimension, weight_col in dimension_map.items():
    x = scenario_summary[weight_col]
    y_rank = scenario_summary["mean_absolute_rank_change"]
    y_rho = scenario_summary["spearman_correlation"]

    rank_corr = pearsonr(x, y_rank).statistic
    rho_corr = pearsonr(x, y_rho).statistic

    dimension_rows.append(
        {
            "dimension": dimension,
            "correlation_weight_vs_mean_abs_rank_change": rank_corr,
            "correlation_weight_vs_spearman": rho_corr,
            "min_weight": x.min(),
            "max_weight": x.max(),
            "baseline_weight": BASELINE_WEIGHTS[weight_col],
        }
    )

dimension_summary = pd.DataFrame(dimension_rows)

# =============================================================================
# 12. CONTROLLED REPRESENTATIVE SCENARIOS
# =============================================================================
print("\nRepresentative scenarios")
print("-" * 80)

representative_definitions = proportional_emphasis_scenarios()
representative_rows = []

for label, weights in representative_definitions:
    complete = features[dimension_cols].notna().all(axis=1)
    score = (
        features[dimension_cols]
        .mul(
            pd.Series(
                {
                    "scale_reach_score": weights["scale_reach_weight"],
                    "quality_score": weights["quality_weight"],
                    "engagement_score": weights["engagement_weight"],
                    "momentum_score": weights["momentum_weight"],
                }
            ),
            axis=1,
        )
        .sum(axis=1)
        .where(complete, np.nan)
    )
    rank = rank_for_scores(score)

    base = pd.DataFrame(
        {
            "primary_publisher": features["primary_publisher"],
            "rank": rank,
            "score": score,
        }
    )
    available = base.merge(
        features[["primary_publisher", "rank", "overall_score"]].rename(
            columns={"rank": "baseline_rank", "overall_score": "baseline_score"}
        ),
        on="primary_publisher",
    ).dropna(subset=["rank", "baseline_rank"])

    top_overlaps = {}
    for n in TOP_N_VALUES:
        scenario_top = set(
            base.dropna(subset=["rank"]).nsmallest(n, "rank")["primary_publisher"]
        )
        top_overlaps[n] = len(baseline_top[n].intersection(scenario_top)) / n

    rho = spearmanr(
        available["baseline_rank"].astype(float),
        available["rank"].astype(float),
    ).statistic

    representative_rows.append(
        {
            "scenario_label": label,
            **weights,
            "weight_distance_from_baseline": float(
                np.sqrt(
                    sum(
                        (weights[k] - BASELINE_WEIGHTS[k]) ** 2
                        for k in BASELINE_WEIGHTS
                    )
                )
            ),
            "mean_absolute_rank_change": available.apply(
                lambda r: abs(r["rank"] - r["baseline_rank"]), axis=1
            ).mean(),
            "spearman_correlation": rho,
            "top_5_overlap": top_overlaps[5],
            "top_10_overlap": top_overlaps[10],
            "top_20_overlap": top_overlaps[20],
        }
    )

representative_summary = pd.DataFrame(representative_rows)

# Top-10 ranks for representative scenarios.
representative_top10 = []
for label, weights in representative_definitions:
    complete = features[dimension_cols].notna().all(axis=1)
    score = (
        features[dimension_cols]
        .mul(
            pd.Series(
                {
                    "scale_reach_score": weights["scale_reach_weight"],
                    "quality_score": weights["quality_weight"],
                    "engagement_score": weights["engagement_weight"],
                    "momentum_score": weights["momentum_weight"],
                }
            ),
            axis=1,
        )
        .sum(axis=1)
        .where(complete, np.nan)
    )
    rank = rank_for_scores(score)
    top = pd.DataFrame(
        {
            "primary_publisher": features["primary_publisher"],
            "rank": rank,
        }
    ).dropna(subset=["rank"]).nsmallest(10, "rank")
    for _, row in top.iterrows():
        representative_top10.append(
            {
                "scenario_label": label,
                "primary_publisher": row["primary_publisher"],
                "rank": int(row["rank"]),
            }
        )
representative_top10 = pd.DataFrame(representative_top10)

# =============================================================================
# 13. VISUALIZATIONS
# =============================================================================
print("\nGenerating plots")
print("-" * 80)

sns.set_theme(style="whitegrid")

# Plot 1: Scenario weight distribution.
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, (label, col) in zip(
    axes.flat,
    [
        ("Scale & Reach", "scale_reach_weight"),
        ("Quality", "quality_weight"),
        ("Engagement", "engagement_weight"),
        ("Growth & Momentum", "momentum_weight"),
    ],
):
    counts = scenarios[col].value_counts().sort_index()
    ax.bar(counts.index * 100, counts.values, width=3.5)
    baseline_pct = BASELINE_WEIGHTS[col] * 100
    ax.axvline(baseline_pct, linestyle="--", linewidth=2, label=f"Baseline: {baseline_pct:.0f}%")
    ax.set_title(label)
    ax.set_xlabel("Weight (%)")
    ax.legend()
fig.suptitle("Tested Top-Level Weight Distribution", y=1.02, fontsize=14)
fig.tight_layout()
fig.savefig(PLOT_DIR / "01_scenario_weight_distribution.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 2: Ranking stability boxplot.
fig, ax = plt.subplots(figsize=(11, 6))
box_data = [
    g["absolute_rank_change"].dropna().to_numpy()
    for _, g in scenario_results.groupby("scenario_id", sort=False)
]
ax.boxplot(box_data, showfliers=False)
ax.set_title("Absolute Publisher Rank Change Across Scenarios")
ax.set_xlabel("Scenario")
ax.set_ylabel("Absolute rank change")
ax.set_xticks(np.arange(1, len(scenarios) + 1))
ax.set_xticklabels(scenarios["scenario_id"], rotation=90)
fig.tight_layout()
fig.savefig(PLOT_DIR / "02_ranking_stability_boxplot.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 3: Scenario similarity to baseline.
fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(
    scenario_summary["weight_distance_from_baseline"],
    scenario_summary["spearman_correlation"],
    s=45,
)
base_row = scenario_summary.loc[scenario_summary["scenario_id"] == BASELINE_SCENARIO_ID].iloc[0]
ax.scatter(
    base_row["weight_distance_from_baseline"],
    base_row["spearman_correlation"],
    s=120,
    marker="*",
    label="Baseline",
)
ax.set_title("Scenario Distance vs. Ranking Similarity to Baseline")
ax.set_xlabel("Euclidean distance from baseline weights")
ax.set_ylabel("Spearman correlation")
ax.legend()
fig.tight_layout()
fig.savefig(PLOT_DIR / "03_scenario_similarity.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 4: Top-N stability.
long_top = scenario_summary[
    ["scenario_id", "weight_distance_from_baseline", "top_5_overlap", "top_10_overlap", "top_20_overlap"]
].melt(
    id_vars=["scenario_id", "weight_distance_from_baseline"],
    value_vars=["top_5_overlap", "top_10_overlap", "top_20_overlap"],
    var_name="top_n",
    value_name="overlap",
)
long_top["top_n"] = long_top["top_n"].str.replace("top_", "Top ").str.replace("_overlap", "")
long_top = long_top.sort_values("weight_distance_from_baseline")
fig, ax = plt.subplots(figsize=(10, 6))
for label, group in long_top.groupby("top_n", sort=False):
    ax.plot(group["weight_distance_from_baseline"], group["overlap"], marker="o", label=label)
ax.set_title("Top-N Retention Relative to Baseline")
ax.set_xlabel("Euclidean distance from baseline weights")
ax.set_ylabel("Baseline Top-N overlap")
ax.set_ylim(0, 1.05)
ax.legend()
fig.tight_layout()
fig.savefig(PLOT_DIR / "04_top_n_stability.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 5: Publisher Top-10 frequency.
top10_freq = publisher_summary.sort_values(
    ["top_10_frequency", "baseline_rank"], ascending=[False, True]
).head(20).iloc[::-1]
fig, ax = plt.subplots(figsize=(10, 8))
ax.barh(top10_freq["primary_publisher"], top10_freq["top_10_frequency"])
ax.set_title("Publishers with the Highest Top-10 Frequency")
ax.set_xlabel("Share of valid scenarios in Top 10")
ax.set_ylabel("Publisher")
ax.set_xlim(0, 1.05)
fig.tight_layout()
fig.savefig(PLOT_DIR / "05_publisher_top10_frequency.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 6: Score sensitivity for baseline Top 10.
baseline_top10_publishers = (
    features.loc[features["rank"].notna()]
    .nsmallest(10, "rank")["primary_publisher"]
    .tolist()
)
score_plot = publisher_summary[
    publisher_summary["primary_publisher"].isin(baseline_top10_publishers)
].copy()
score_plot = score_plot.sort_values("baseline_rank")
fig, ax = plt.subplots(figsize=(11, 6))
x = np.arange(len(score_plot))
lower = score_plot["baseline_score"] - score_plot["min_score"]
upper = score_plot["max_score"] - score_plot["baseline_score"]
ax.errorbar(
    x,
    score_plot["baseline_score"],
    yerr=[lower, upper],
    fmt="o",
    capsize=5,
)
ax.set_xticks(x)
ax.set_xticklabels(score_plot["primary_publisher"], rotation=45, ha="right")
ax.set_ylabel("Overall score")
ax.set_title("Score Sensitivity for Baseline Top 10 Publishers")
fig.tight_layout()
fig.savefig(PLOT_DIR / "06_publisher_score_sensitivity.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 7: Rank sensitivity heatmap for baseline Top 20 across representative scenarios.
heatmap_publishers = (
    features.loc[features["rank"].notna()]
    .nsmallest(20, "rank")["primary_publisher"]
    .tolist()
)
heat = pd.DataFrame(index=heatmap_publishers)
for label, weights in representative_definitions:
    complete = features[dimension_cols].notna().all(axis=1)
    score = (
        features[dimension_cols]
        .mul(
            pd.Series(
                {
                    "scale_reach_score": weights["scale_reach_weight"],
                    "quality_score": weights["quality_weight"],
                    "engagement_score": weights["engagement_weight"],
                    "momentum_score": weights["momentum_weight"],
                }
            ),
            axis=1,
        )
        .sum(axis=1)
        .where(complete, np.nan)
    )
    rank = rank_for_scores(score)
    heat[label] = features["primary_publisher"].map(
        pd.Series(rank.to_numpy(), index=features["primary_publisher"])
    )
heat["Baseline"] = features.set_index("primary_publisher").loc[
    heat.index, "rank"
]
heat = heat[["Baseline", "SCALE_REACH", "QUALITY", "ENGAGEMENT", "MOMENTUM"]]
fig, ax = plt.subplots(figsize=(10, 11))
im = ax.imshow(heat.to_numpy(dtype=float), aspect="auto", interpolation="nearest")
ax.set_xticks(np.arange(heat.shape[1]))
ax.set_xticklabels(heat.columns)
ax.set_yticks(np.arange(heat.shape[0]))
ax.set_yticklabels(heat.index)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        value = heat.iloc[i, j]
        if pd.notna(value):
            ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=8)
fig.colorbar(im, ax=ax, label="Rank")
ax.set_title("Ranks Across Baseline and Representative Weighting Scenarios")
ax.set_xlabel("Scenario")
ax.set_ylabel("Baseline Top-20 publisher")
fig.tight_layout()
fig.savefig(PLOT_DIR / "07_rank_sensitivity_heatmap.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Plot 8: Dimension weight vs ranking sensitivity.
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
for ax, (label, col) in zip(axes.flat, dimension_map.items()):
    x = scenario_summary[col].to_numpy()
    y = scenario_summary["mean_absolute_rank_change"].to_numpy()
    ax.scatter(x, y, s=40)
    if len(np.unique(x)) > 1:
        slope, intercept = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        ax.plot(x_line, slope * x_line + intercept, linewidth=2)
    ax.axvline(BASELINE_WEIGHTS[col], linestyle="--", linewidth=1.5)
    ax.set_title(label)
    ax.set_xlabel("Top-level weight")
    ax.set_ylabel("Mean absolute rank change")
fig.suptitle(
    "Dimension Weight vs. Ranking Sensitivity\n"
    "Association within the constrained scenario grid; not a causal estimate",
    y=1.02,
    fontsize=13,
)
fig.tight_layout()
fig.savefig(PLOT_DIR / "08_dimension_weight_vs_rank_sensitivity.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# =============================================================================
# 14. SAVE CSV OUTPUTS
# =============================================================================
print("\nSaving CSV outputs")
print("-" * 80)

scenario_results.to_csv(
    OUTPUT_DIR / "publisher_sensitivity_results.csv", index=False
)
publisher_summary.to_csv(
    OUTPUT_DIR / "publisher_sensitivity_summary.csv", index=False
)
scenario_summary.to_csv(
    OUTPUT_DIR / "scenario_sensitivity_summary.csv", index=False
)
dimension_summary.to_csv(
    OUTPUT_DIR / "dimension_sensitivity_summary.csv", index=False
)

# Additional representative output makes the controlled tests reproducible.
representative_summary.to_csv(
    OUTPUT_DIR / "representative_scenario_summary.csv", index=False
)
representative_top10.to_csv(
    OUTPUT_DIR / "representative_scenario_top10.csv", index=False
)

print("Saved required CSV outputs plus representative-scenario CSVs.")

# =============================================================================
# 15. FINAL VALIDATION
# =============================================================================
print("\nFinal validation")
print("-" * 80)

# Scenario structure.
assert scenarios["scenario_id"].is_unique
assert not scenarios[list(BASELINE_WEIGHTS)].duplicated().any()
assert np.isclose(
    scenarios[list(BASELINE_WEIGHTS)].sum(axis=1), 1.0, atol=1e-10
).all()

# Scenario-level completeness.
expected_rows = valid_count * publisher_count
assert len(scenario_results) == expected_rows
assert not scenario_results.duplicated(
    ["scenario_id", "primary_publisher"]
).any()

# Score range.
non_nan_scores = scenario_results["overall_score"].dropna()
assert non_nan_scores.between(0, 1).all()

# Ranking order validation within each scenario.
for scenario_id, group in scenario_results.groupby("scenario_id", sort=False):
    valid_group = group.dropna(subset=["overall_score", "rank"]).sort_values(
        "overall_score", ascending=False
    )
    expected_rank = rank_for_scores(valid_group["overall_score"])
    if not np.array_equal(
        expected_rank.to_numpy(dtype=float),
        valid_group["rank"].to_numpy(dtype=float),
    ):
        raise AssertionError(f"Ranking validation failed for {scenario_id}.")

validate_no_inf(scenario_results, "publisher_sensitivity_results")
validate_no_inf(publisher_summary, "publisher_sensitivity_summary")
validate_no_inf(scenario_summary, "scenario_sensitivity_summary")
validate_no_inf(dimension_summary, "dimension_sensitivity_summary")

print(f"Scenario observations: {len(scenario_results):,}")
print(f"Expected observations: {expected_rows:,}")
print(f"Publisher/scenario duplicates: {scenario_results.duplicated(['scenario_id', 'primary_publisher']).sum()}")
print(f"Scenario score values within [0,1]: {non_nan_scores.between(0,1).all()}")
print(f"Publishers with missing overall score in every scenario: {features['overall_score'].isna().sum()}")

# =============================================================================
# 16. FINAL SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("FINAL ANALYSIS SUMMARY")
print("=" * 80)

valid_summary = scenario_summary.dropna(subset=["spearman_correlation"])

print(f"Publishers: {publisher_count}")
print(f"Candidate combinations: {candidate_count}")
print(f"Valid scenarios: {valid_count}")
print(f"Invalid combinations removed: {invalid_count}")

print("\nBaseline Top 10:")
print(
    features.loc[features["rank"].notna()]
    .nsmallest(10, "rank")[
        ["primary_publisher", "overall_score", "rank",
         "scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
    ]
    .to_string(index=False)
)

print("\nRanking stability:")
print(f"Mean absolute rank change across all scenario-publisher observations: {scenario_results['absolute_rank_change'].mean():.3f}")
print(f"Minimum Spearman correlation: {valid_summary['spearman_correlation'].min():.6f}")
print(f"Median Spearman correlation: {valid_summary['spearman_correlation'].median():.6f}")
print(f"Maximum Spearman correlation: {valid_summary['spearman_correlation'].max():.6f}")

largest = scenario_results.dropna(subset=["absolute_rank_change"]).nlargest(
    10, "absolute_rank_change"
)
print("\nLargest observed rank movements:")
print(
    largest[
        ["scenario_id", "primary_publisher", "baseline_rank", "rank",
         "rank_change", "absolute_rank_change"]
    ].to_string(index=False)
)

print("\nTop-N overlap statistics across scenarios:")
for n in TOP_N_VALUES:
    col = f"top_{n}_overlap"
    print(
        f"Top {n}: min={scenario_summary[col].min():.3f}, "
        f"median={scenario_summary[col].median():.3f}, "
        f"max={scenario_summary[col].max():.3f}"
    )

print("\nMost stable publishers by smallest rank range (baseline Top 10):")
print(
    publisher_summary[
        publisher_summary["baseline_rank"] <= 10
    ].sort_values(["rank_range", "mean_absolute_rank_change"])[
        ["primary_publisher", "baseline_rank", "rank_range",
         "score_range", "mean_absolute_rank_change", "top_10_frequency"]
    ].to_string(index=False)
)

print("\nMost sensitive publishers by largest rank range:")
print(
    publisher_summary.sort_values(
        ["rank_range", "mean_absolute_rank_change"],
        ascending=[False, False],
    ).head(10)[
        ["primary_publisher", "baseline_rank", "rank_range",
         "score_range", "mean_absolute_rank_change", "top_10_frequency"]
    ].to_string(index=False)
)

print("\nDimension-level associations:")
print(dimension_summary.to_string(index=False))

print("\nRepresentative scenarios:")
print(representative_summary.to_string(index=False))

print("\nRepresentative scenario Top 10:")
print(
    representative_top10.pivot(
        index="primary_publisher", columns="scenario_label", values="rank"
    ).sort_index().to_string()
)

print("\nOutput directory:", OUTPUT_DIR.resolve())
print("Plot directory:", PLOT_DIR.resolve())
print("\nAnalysis completed successfully.")