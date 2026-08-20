"""
Build publisher_features.csv from master_dataset.csv: one row per
primary_publisher, aggregating game-level data into 8 features. Publishers
with fewer than MIN_GAMES titles are dropped (too few games for a
publisher-level average to be meaningful/stable).

Features (all aggregated per publisher):
  - review_score            : mean of review_score (0-9), EXCLUDING 0 --
                               0 signals "too few reviews to score", not an
                               actually bad score, so including it would
                               wrongly drag the average down for a publisher
                               that's simply under-reviewed, not disliked.
  - avg_owners_mid           : mean of owners_mid (reach per game)
  - avg_language_count       : mean of language_count (localization reach)
  - avg_positive_review_ratio: mean of positive/(positive+negative) per game
                               (already 0-1, games with zero reviews at all
                               are NaN and excluded from the mean, not
                               treated as 0% positive)
  - avg_active_users_rate    : mean of concurrent_users_yesterday/owners_mid
                               per game (already conceptually 0-1, but see
                               normalization note below -- it isn't reliably
                               bounded in this data)
  - recent_release_count     : count of games released within RECENT_YEARS
                               of the dataset's own max release_date
  - recent_release_ratio     : recent_release_count / game_count (0-1)
  - game_count               : portfolio size (games per publisher)

Normalization (proposed and applied -- see module-level summary in chat):
  - avg_owners_mid, avg_language_count, game_count, recent_release_count
      -> log1p + min-max. These are count/count-derived aggregates and are
         heavily right-skewed (a few large publishers, many small ones);
         log1p compresses the tail before scaling to [0,1]. Method choice
         is confirmed by computed skew on THIS aggregated data (>2 -> log),
         not assumed.
  - avg_active_users_rate
      -> percentile rank, not log+min-max. This ratio is not reliably
         bounded in the source data -- a handful of games have
         steamspy-bucket-mismatched owners_mid producing rates that even
         log1p doesn't tame, which would crush every other publisher
         toward 0 after min-max. Percentile rank is immune to how extreme
         an outlier is.
  - review_score (0-9), avg_positive_review_ratio, recent_release_ratio
      -> left as-is. Already bounded and directly interpretable; scaling
         them further would only obscure the original scale for no
         analytical benefit.
"""

import zipfile
import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "data/processed/master_dataset.zip"
OUT = "data/processed/publisher_features.csv"
MIN_GAMES = 10
RECENT_YEARS = 2


with zipfile.ZipFile(SRC) as z:
    with z.open("master_dataset.csv") as f:
        df = pd.read_csv(f, low_memory=False)
print("Loaded master_dataset.csv:", df.shape)

# ---------------------------------------------------------------------------
# PER-GAME PREP (before aggregating)
# ---------------------------------------------------------------------------
review_denom = df["positive"] + df["negative"]
df["review_positive_ratio"] = np.where(review_denom > 0, df["positive"] / review_denom, np.nan)
df["active_users_rate"] = np.where(df["owners_mid"] > 0, df["concurrent_users_yesterday"] / df["owners_mid"], np.nan)

df["release_date_parsed"] = pd.to_datetime(df["release_date"], errors="coerce")
reference_today = df["release_date_parsed"].max()
df["is_recent"] = (reference_today - df["release_date_parsed"]).dt.days / 365.25 <= RECENT_YEARS
print(f"Reference 'today' (max release_date in data): {reference_today.date()}")

# review_score: 0 means "too few reviews to compute a score", not "bad" --
# treat as missing for averaging purposes, not as a real 0.
df["review_score_for_avg"] = df["review_score"].replace(0, np.nan)

# rows with no primary_publisher can't be aggregated -- report, don't guess
missing_pub = df["primary_publisher"].isna().sum()
print(f"Rows with missing primary_publisher (excluded from aggregation): {missing_pub} ({missing_pub/len(df)*100:.1f}%)")

# ---------------------------------------------------------------------------
# AGGREGATE TO PUBLISHER LEVEL
# ---------------------------------------------------------------------------
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

print(f"\nPublishers before game_count filter: {len(publisher_features)}")
publisher_features = publisher_features[publisher_features["game_count"] >= MIN_GAMES].copy()
print(f"Publishers with game_count >= {MIN_GAMES}: {len(publisher_features)}")

# ---------------------------------------------------------------------------
# NORMALIZATION (method chosen per feature, justified above; skew computed
# live on this aggregated/filtered data, not assumed)
# ---------------------------------------------------------------------------
SKEW_THRESHOLD = 2.0
log_minmax_candidates = ["avg_owners_mid", "avg_language_count", "game_count", "recent_release_count"]
rank_scaled = ["avg_active_users_rate"]

print("\nNormalization applied:")
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
    print(f"  {col:24s} skew={col_skew:7.2f}  method={method}")

for col in rank_scaled:
    publisher_features[col + "_norm"] = publisher_features[col].rank(pct=True)
    print(f"  {col:24s}              method=percentile rank")

print("\nLeft unnormalized (already bounded/interpretable): review_score (0-9), "
      "avg_positive_review_ratio (0-1), recent_release_ratio (0-1)")

# ---------------------------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)
print("shape:", publisher_features.shape)
print("duplicate publishers:", publisher_features["primary_publisher"].duplicated().sum())
inf_check = np.isinf(publisher_features.select_dtypes(include=[np.number])).sum()
print("columns with inf/-inf:", inf_check[inf_check > 0].to_dict() or "none")
print("\nmissing % per column:")
print((publisher_features.isna().mean() * 100).round(2).to_string())

print("\nTop 10 by review_score (min 10 games, 0s excluded from average):")
print(publisher_features.nlargest(10, "review_score")[["primary_publisher", "game_count", "review_score"]].to_string(index=False))

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
publisher_features.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={publisher_features.shape}")
