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

SRC = "./master_dataset.csv"
OUT = "./publisher_features.csv"
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

SRC = "./publisher_features.csv"
OUT = "./publisher_scores.csv"

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
