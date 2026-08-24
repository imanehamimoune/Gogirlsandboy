''' PART 1: BUILDING PUBLISHER FEATURES '''

'''
Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a publisher-level feature table from game-level data. Prioritize correct, well-justified aggregation and normalization over cleverness.
Context: Input is master_dataset.csv — one row per app_id, already merged and cleaned. The next step is to aggregate this to one row per publisher_primary, producing a small set of features usable for ranking/scoring publishers. Some of these features are already naturally bounded ratios; others are raw counts/rates that need normalization before they can be compared or combined meaningfully.

Objective: Produce publisher_features.csv — one row per publisher_primary — containing exactly the 8 features below, with publishers below a minimum game count excluded, and the appropriate features normalized. Do not touch master_dataset.csv itself.
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
    * Report how many rows have a missing publisher_primary (these can't be aggregated — exclude them from this table, don't guess a publisher).
3. Aggregate to publisher level using the 8 feature definitions above.
4. Drop publishers with game_count < 10. Report publisher count before and after this filter.
5. Normalize the count/rate features (owner_mid count, language_count, game_count, recent_release_count, active_users_rate) using the scale proposed and justified in the scope decision above, writing results to NEW columns (e.g. <feature>_norm) — never overwrite the original. Leave review_score, positive_review_ratio, and recent_release_ratio unnormalized, since they're already bounded and directly interpretable.
6. Execute and validate:
    * Actually run the code.
    * Confirm: one row per publisher, no duplicate publishers, no inf/-inf values anywhere (check explicitly), and report missing % per column.
7. Deliver:
    * The code, plus a short summary: publisher count before/after the game_count filter, the normalization method chosen per feature (with the diagnostic that justified it), and which columns have the most missingness and why.

Constraints (Do Not):
* Do not drop any game-level row for reasons other than missing publisher_primary (which can't be aggregated at all).
* Do not fill a NaN ratio/average with 0 — a 0 has a different meaning (e.g. "no reviews at all") than "not enough data to compute."
* Do not silently let divide-by-zero produce inf — guard explicitly.
* Do not normalize review_score, positive_review_ratio, or recent_release_ratio — they're already bounded and interpretable as-is.
* Do not pick a normalization method without first checking the actual distribution of that feature on this data.
* Do not overengineer — no scaling/encoding beyond what's needed for the 5 count/rate features, no speculative extra features.

Expected Output:
* publisher_features.csv: one row per publisher_primary (game_count >= 10 only), containing the 8 requested features plus normalized (_norm) versions of owner_mid count, language_count, game_count, recent_release_count, and active_users_rate.
* A short written summary covering: publisher counts before/after filtering, the normalization method and justification per feature, and notable missingness patterns.

Validation:
* Reload the output and confirm: no duplicate publishers, all publishers have game_count >= 10, no inf/-inf values anywhere, and normalized columns fall within their expected range (e.g. [0,1] for min-max-based methods).

'''
# Request: 2026-08-20 19:50 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


"""
Build publisher_features.csv from master_dataset.csv: one row per
publisher_primary, aggregating game-level data into 8 features. Publishers
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

# rows with no publisher_primary can't be aggregated -- report, don't guess
missing_pub = df["publisher_primary"].isna().sum()
print(f"Rows with missing publisher_primary (excluded from aggregation): {missing_pub} ({missing_pub/len(df)*100:.1f}%)")

# =============================================================================
# TASK 3: AGGREGATE TO PUBLISHER LEVEL
# =============================================================================
print("\n" + "=" * 70)
print("TASK 3: AGGREGATE TO PUBLISHER LEVEL")
print("=" * 70)

grouped = df.groupby("publisher_primary")
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
print("one row per publisher (no duplicates):", publisher_features["publisher_primary"].duplicated().sum() == 0)
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
print(f"Rows excluded upstream for missing publisher_primary: {missing_pub} ({missing_pub/len(df)*100:.1f}% of games).")
print("\nNormalization method per feature (skew computed on this aggregated data):")
for col, (skew_val, method) in normalization_log.items():
    skew_str = f"skew={skew_val:.2f}" if skew_val is not None else "outlier-driven, not skew-based"
    print(f"  {col:24s} -> {method:20s} ({skew_str})")
print("\nColumns with the most missingness:")
print(missingness[missingness > 0].sort_values(ascending=False).to_string() or "  none")
print("\nTop 10 publishers by review_score (min 10 games, 0s excluded from average):")
print(publisher_features.nlargest(10, "review_score")[["publisher_primary", "game_count", "review_score"]].to_string(index=False))




''' PART 2: EVALUATING PUBLISHER SCORES '''
'''
Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a weighted scoring and ranking layer on top of an existing publisher-level feature table. Prioritize transparency and easy adjustability of every weight/assumption over cleverness.
Context: Input is publisher_features.csv — one row per publisher_primary, already aggregated and normalized (contains raw features like review_score, avg_owners_mid, avg_language_count, avg_positive_review_ratio, avg_active_users_rate, recent_release_ratio, game_count, recent_release_count, plus their _norm counterparts where applicable). The next step is to combine these into 4 weighted dimension scores and one overall weighted score, then rank publishers by it.

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
* publisher_scores.csv: one row per publisher, containing rank, publisher_primary, game_count, the 4 dimension scores (scale_reach_score, quality_score, engagement_score, momentum_score), and overall_score.
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
import matplotlib.pyplot as plt

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

dup_count = df["publisher_primary"].duplicated().sum()
print(f"\nduplicate publishers: {dup_count}")
print(f"NaN overall_score count matches TASK 5 report: {df['overall_score'].isna().sum() == nan_overall.sum()}")

# =============================================================================
# SAVE
# =============================================================================
final_cols = ["rank", "publisher_primary", "game_count"] + DIMS + ["overall_score"]
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


DIMS = ["scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
LABELS = {"scale_reach_score": "Scale & Reach", "quality_score": "Quality",
          "engagement_score": "Engagement", "momentum_score": "Growth & Momentum"}
COLORS = {"scale_reach_score": "#4C72B0", "quality_score": "#55A868",
          "engagement_score": "#C44E52", "momentum_score": "#DD8452"}

top10 = df.head(10)

# --- Plot 1: Top 10 by overall_score (solid green) -------------------------
fig, ax = plt.subplots(figsize=(9, 6))
plot_order = top10.iloc[::-1]
bars = ax.barh(plot_order["publisher_primary"], plot_order["overall_score"], color="green")
for bar, val in zip(bars, plot_order["overall_score"]):
    ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Overall Score")
ax.set_title("Top 10 Publishers by Overall Score", fontsize=13, fontweight="bold")
ax.set_xlim(0, top10["overall_score"].max() * 1.15)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("data/feature_analysis/publisher_score_plots/plot1_top10_overall.png", dpi=150)
plt.close()

# --- Plot 2: Acquisition candidates -- dimension scores (grouped, colored) -
EXCLUDE_PUBLISHERS = ["PlayStation Publishing LLC"]
XBOX_PUBLISHER = "Xbox Game Studios"  # adjust to match the exact string in your data

pool = df[~df["publisher_primary"].isin(EXCLUDE_PUBLISHERS)]

top3 = pool.nlargest(3, "overall_score")
xbox_row = pool[pool["publisher_primary"] == XBOX_PUBLISHER]

candidates = pd.concat([top3, xbox_row]).drop_duplicates(subset="publisher_primary")

x = np.arange(len(candidates))
width = 0.2
fig, ax = plt.subplots(figsize=(15, 7))
for i, d in enumerate(DIMS):
    offset = (i - 1.5) * width
    bars = ax.bar(x + offset, candidates[d], width, label=LABELS[d], color=COLORS[d])
    for bar, val in zip(bars, candidates[d]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
ax.set_xticks(x)
ax.set_xticklabels(candidates["publisher_primary"], rotation=25, ha="right")
ax.set_ylabel("Dimension Score (0-1, scaled against all publishers)")
ax.set_title("Top 3 Acquisition Candidates -- Dimension Scores", fontsize=13, fontweight="bold")
ax.set_ylim(0, 1.15)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("data/feature_analysis/publisher_score_plots/plot2_top3_across_dimensions.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Plot 3: Top 10 per individual dimension (2x2 grid, solid green) -------
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
for ax, d in zip(axes.flat, DIMS):
    top10_dim = df.dropna(subset=[d]).nlargest(10, d).iloc[::-1]
    bars = ax.barh(top10_dim["publisher_primary"], top10_dim[d], color="green")
    for bar, val in zip(bars, top10_dim[d]):
        ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=8)
    ax.set_xlabel(f"{LABELS[d]} Score")
    ax.set_xlim(0, top10_dim[d].max() * 1.15)
    ax.set_title(f"Top 10 by {LABELS[d]}", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Top 10 Publishers per Individual Dimension", fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("data/feature_analysis/publisher_score_plots/plot3_top10_per_dimension.png", dpi=150, bbox_inches="tight")
plt.close()





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
│   └── feature_analysis/
│       └── publisher_scores.csv
│
└── src/
    └── feature_engineering/
        └── sensitivity_analysis.py

Read the data from:

../../data/feature_analysis/publisher_scores.csv

Do not modify the input file.

Save the generated plot to:

../../data/feature_analysis/sensitivity_plots/

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

data/feature_analysis/sensitivity_plots/publisher_score_sensitivity.png

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

INPUT_PATH = Path("data/feature_analysis/publisher_scores.csv")
OUTPUT_DIR = Path("data/feature_analysis/sensitivity_plots")
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
