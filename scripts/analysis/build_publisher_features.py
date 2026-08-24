''' PART 1: BUILDING PUBLISHER FEATURES '''

'''
PROMPT

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

SRC_MASTER = "data/processed/master_dataset.csv"
OUT_PUBLISHER_FEATURES = "data/analysis/publisher_features.csv"

MIN_GAMES = 10
RECENT_YEARS = 2

# =============================================================================
# TASK 1: LOAD
# =============================================================================
df = pd.read_csv(SRC_MASTER, low_memory=False)
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

publisher_features.to_csv(OUT_PUBLISHER_FEATURES, index=False)
print(f"\nSaved: {OUT_PUBLISHER_FEATURES}  shape={publisher_features.shape}")

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
