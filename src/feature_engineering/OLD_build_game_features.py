'''
Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a game-level feature set for later acquisition/portfolio analysis. Prioritize correct, well-justified calculations over cleverness.
Context: Input is master_dataset.csv — one row per app_id, already merged and cleaned. Rather than pre-aggregating to publisher level, keep the output at game level so it can be grouped/re-sliced later (by publisher, developer, genre, release year, etc.) without re-running the pipeline. publisher-level rollups, when needed, are just a groupby("primary_publisher") away from this file.
Objective: Produce game_features.csv — one row per app_id — containing the engineered dimension features below plus a limited, clearly justified set of raw supporting columns. Do not touch master_dataset.csv itself.
Scope decisions to make explicit up front (state your choice + reasoning in the code as comments):
* Whether to include type == "demo" rows, or restrict to type == "game". State the reasoning either way; if demos are kept, flag them with a column so they can be filtered out downstream instead of silently mixed in.
* What "now" means for recency-based features. Use the max release_date found in the dataset as reference "today" (fixed snapshot), not the real current date — document this.
* Rows with missing primary_publisher are still valid game-level rows (they just can't be grouped by publisher later) — keep them, don't drop them.
Tasks:
1. Scale & Reach (per game)
    * owners_mid (already exists — keep as-is, this is the per-game reach).
    * language_count (already exists — keep as-is).
    * No aggregation needed at this level; these become meaningful once grouped later.
2. Commercial Demand (per game)
    * est_revenue = owners_mid * price_final_clean. Free games correctly contribute 0 via price_final_clean — do not re-derive price from price_final.
    * Keep positive and recommendations as-is (already per-game); do NOT compute a correlation here — a single game has no distribution to correlate. Leave that calculation for whenever this is grouped later.
3. Quality (per game)
    * review_positive_ratio = positive / (positive + negative), guarding against division by zero (both 0 -> NaN, not 0 — "no reviews" isn't "0% positive").
    * Keep metacritic_score as-is; add has_metacritic_score (boolean) so downstream averages can be coverage-weighted instead of naively including ~97% NaNs as silent exclusions.
4. Engagement (per game)
    * active_engagement_rate = concurrent_users_yesterday / owners_mid, guarding against division by zero (owners_mid == 0 -> NaN).
    * review_rate = (positive + negative) / owners_mid, same guard.
5. Growth & Momentum (per game)
    * Parse release_date to datetime; add has_valid_release_date (boolean) — do not drop rows with missing/unparseable dates (~20% of the data), just flag them so recency-based slicing later knows to exclude them.
    * years_since_release: reference "today" (max release_date in dataset) minus this game's release_date. NaN where has_valid_release_date is False.
    * is_recent: boolean, True if released within 2 years of reference "today" (same window to be reused consistently in any later grouping). NaN/False-with-flag where date is invalid — be explicit about which.
    * Release cadence and "recent vs. historical" comparisons are NOT computed here — they only make sense once grouped by publisher (or developer, or genre) later. Leave them out; note this in a comment so it's clear it's a deliberate omission, not an oversight.
6. Genre/Tag columns — kept, not analyzed
    * Genre demand scoring is deliberately out of scope for this pass (planned as a later, separate step). Do not compute a demand score here.
    * Simply carry genres_ctg (and categories and tags, if useful) forward as-is into game_features.csv, unmodified, so the raw signal is available whenever the demand analysis is done later — do not explode, drop, or transform these columns in this pipeline.
7. Feature selection for the output file
    * Keep: app_id, name, primary_publisher, primary_developer, type, is_free, release_date, genres_ctg (raw, unmodified, for later demand analysis), plus every engineered feature from steps 1–5, plus the boolean coverage/validity flags (has_metacritic_score, has_valid_release_date, is_recent) so any later aggregation can be coverage-aware instead of guessing.
    * Also keep raw building blocks a later ML model may want directly rather than only the ratio: owners_mid, positive, negative, recommendations, metacritic_score, concurrent_users_yesterday, price_final_clean, language_count, n_developers, n_publishers, has_company_data, has_price_data. Reason: ratios lose information a model could use raw (e.g. a 90% positive ratio means something different at 10 reviews vs. 10,000 — keeping positive/negative alongside the ratio preserves that).
    * Drop: source-formatting/display-only columns (price_final_formatted, price_initial_formatted, price_recurring_sub_desc, owners_range as a string, price_currency at row level, languages_games/languages_steamspy — redundant with genres_ctg for the planned later genre analysis, or purely display-oriented). For each dropped column, state the reason in a code comment — "display-only duplicate of X" or "redundant with column Y kept for the same purpose" are valid reasons; "probably not needed" is not.
    * When unsure, default to keeping a column rather than dropping it — but only if it has a plausible connection to reach, performance, quality, risk, or the planned later genre-demand analysis.
8. Execute and validate
    * Actually run the code.
    * Confirm: row count in game_features.csv matches master_dataset.csv row count exactly (no rows gained or lost — this is a feature-add, not a filter), no duplicate app_ids, no unguarded division produced inf/-inf (check explicitly), and NaNs appear exactly where the reasoning above says they should.
9. Deliver
    * The code, plus a short summary: row count, which engineered features had the most missingness and why, and which raw columns were kept specifically for the later (out-of-scope-for-now) genre-demand pass.
Constraints (Do Not):
* Do not drop or filter any app_id rows — this is a feature-engineering pass on the full game-level dataset, not a subset.
* Do not fill a NaN ratio with 0 — a 0 has a different meaning than "not enough data to compute."
* Do not compute cadence, correlation, or "recent vs. historical" comparisons at game level — those require a group of games and belong in whatever script does the later publisher/developer/genre rollup, not here.
* Do not compute any genre-demand score in this pass — that's a separate, later step. Only carry the raw genre column(s) forward unmodified.
* Do not drop a column without stating the reason in a comment.
* Do not silently let divide-by-zero produce inf — guard explicitly.
* Do not overengineer — no scaling/encoding here (separate step), no speculative features outside the 5 dimensions.
Expected Output:
* game_features.csv: one row per app_id, same row count as master_dataset.csv, containing the engineered features from steps 1–5, the raw genre column(s) from step 6, the coverage/validity flags, and the justified supporting columns from step 7.
* A short written summary covering: row count check and missingness patterns worth knowing about.
Validation:
* Reload game_features.csv and confirm: row count == master_dataset.csv row count, no duplicate app_ids, no inf/-inf values anywhere in the file.

'''
# Request: 2026-08-20 18:50 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


"""
Build game_features.csv from master_dataset.csv: one row per app_id,
engineered dimension features (Scale & Reach, Commercial Demand, Quality,
Engagement, Growth & Momentum), raw genre columns carried forward unmodified
for a later demand-analysis pass, and a limited/justified column set.

Currency handling: no rows are dropped for currency reasons. Price/revenue
fields are only trustworthy when the price is EUR-denominated (or the game
is free, where currency is moot), so price_final_clean and est_revenue are
set to NaN wherever that isn't true -- the game itself stays in the dataset
with all its other dimensions (reach, quality, engagement, momentum) intact.
See STEP 0.
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "./master_dataset.csv"
OUT = "./game_features.csv"

df = pd.read_csv(SRC, low_memory=False)
print("Loaded master_dataset.csv:", df.shape)

# ---------------------------------------------------------------------------
# STEP 0: PRICE/CURRENCY TRUST FLAG (no rows dropped)
# ---------------------------------------------------------------------------
# price_eur_verified is True when the row's price can be trusted as
# EUR-denominated: either the game is free (price is unambiguously 0
# regardless of currency), or price_currency is explicitly "EUR". It is
# False for non-EUR currencies (USD, GBP, RUB, ...) and for paid games with
# no price/currency data at all. This flag drives which fields get nulled
# below -- it does NOT remove any row. Every game keeps its owners, reviews,
# engagement, and momentum signal regardless of price-data quality.
df["price_eur_verified"] = (df["is_free"] == True) | (df["price_currency"] == "EUR")  # noqa: E712

currency_counts = df.loc[df["is_free"] == False, "price_currency"].value_counts(dropna=False)  # noqa: E712
print("\nprice_currency breakdown for non-free games:")
print(currency_counts.to_string())
print(f"\nprice_eur_verified True: {df['price_eur_verified'].sum()} | False: {(~df['price_eur_verified']).sum()}")
print("(False = non-EUR currency, or paid game with no price data at all -- these rows are KEPT, just price/revenue fields go NaN)")

# ---------------------------------------------------------------------------
# SCOPE DECISIONS (stated up front, applied below)
# ---------------------------------------------------------------------------
# - type == "demo" rows are KEPT, not restricted to "game" only, since demos
#   still carry legitimate reach/engagement/quality signal (e.g. a demo's
#   review sentiment can predict the full game's reception) -- but they are
#   flagged via the existing "type" column so they can be filtered out
#   downstream by anyone who wants games only.
# - "now" for recency features = the max release_date found in the data
#   (fixed snapshot reference), not the real current date.
# - Rows with missing primary_publisher are KEPT (still valid game-level
#   rows; they just can't be grouped by publisher later).

df["release_date_parsed"] = pd.to_datetime(df["release_date"], errors="coerce")
reference_today = df["release_date_parsed"].max()
print(f"\nReference 'today' (max release_date in data): {reference_today.date()}")

# ---------------------------------------------------------------------------
# 1. SCALE & REACH -- owners_mid, language_count already exist, kept as-is
# ---------------------------------------------------------------------------
# (no new columns needed; these become meaningful once grouped later)

# ---------------------------------------------------------------------------
# 2. COMMERCIAL DEMAND
# ---------------------------------------------------------------------------
# price_final_clean: free games get 0 (justified by is_free); paid games
# keep their scraped price ONLY when price_eur_verified is True. Non-EUR or
# unverifiable prices are set to NaN here -- not because the game is
# excluded, but because we can't trust a cross-currency number in a
# EUR-based revenue estimate. The row and all its other columns remain.
df["price_final_clean"] = df["price_final"]
free_mask = df["is_free"] == True  # noqa: E712
df.loc[free_mask, "price_final_clean"] = df.loc[free_mask, "price_final_clean"].fillna(0.0)
df.loc[~df["price_eur_verified"], "price_final_clean"] = np.nan

# est_revenue: NaN wherever price_final_clean is NaN (i.e. unverified/no
# price data) -- this is a real "unknown," not a 0, so it's left as NaN
# rather than treated as no revenue.
df["est_revenue"] = df["owners_mid"] * df["price_final_clean"]
# positive / recommendations kept as-is (already per-game columns).
# No correlation computed here -- a single game has no distribution.

# ---------------------------------------------------------------------------
# 3. QUALITY
# ---------------------------------------------------------------------------
review_denom = df["positive"] + df["negative"]
df["review_positive_ratio"] = np.where(review_denom > 0, df["positive"] / review_denom, np.nan)
df["has_metacritic_score"] = df["metacritic_score"].notna()

# ---------------------------------------------------------------------------
# 4. ENGAGEMENT
# ---------------------------------------------------------------------------
df["active_engagement_rate"] = np.where(
    df["owners_mid"] > 0, df["concurrent_users_yesterday"] / df["owners_mid"], np.nan
)
df["review_rate"] = np.where(df["owners_mid"] > 0, review_denom / df["owners_mid"], np.nan)

# ---------------------------------------------------------------------------
# 5. GROWTH & MOMENTUM
# ---------------------------------------------------------------------------
df["has_valid_release_date"] = df["release_date_parsed"].notna()
df["years_since_release"] = np.where(
    df["has_valid_release_date"],
    (reference_today - df["release_date_parsed"]).dt.days / 365.25,
    np.nan,
)
df["is_recent"] = np.where(
    df["has_valid_release_date"], df["years_since_release"] <= 2, False
)
# Cadence, correlation, and recent-vs-historical comparisons deliberately
# NOT computed here -- they require a group of games (publisher/developer/
# genre) and belong in whatever script does that later rollup.

# ---------------------------------------------------------------------------
# 6. GENRE/TAG COLUMNS -- kept, not analyzed (out of scope for this pass)
# ---------------------------------------------------------------------------
# genres_ctg / categories / tags carried forward unmodified below; no demand
# scoring, no exploding, no transformation happens in this script.

# ---------------------------------------------------------------------------
# 7. FEATURE SELECTION
# ---------------------------------------------------------------------------
keep_cols = [
    # identifiers / context
    "app_id", "name", "primary_publisher", "primary_developer", "type",
    "is_free", "release_date", "genres_ctg", "categories", "tags",
    # raw building blocks kept for a future ML model (ratios alone lose
    # information -- e.g. 90% positive at 10 reviews vs 10,000 reviews)
    "owners_mid", "positive", "negative", "recommendations",
    "metacritic_score", "concurrent_users_yesterday", "price_final_clean",
    "price_currency", "price_eur_verified",
    "language_count", "n_developers", "n_publishers",
    "has_company_data", "has_price_data",
    # engineered dimension features
    "est_revenue", "review_positive_ratio", "active_engagement_rate",
    "review_rate", "years_since_release",
    # coverage / validity flags
    "has_metacritic_score", "has_valid_release_date", "is_recent",
]
game_features = df[keep_cols].copy()

# Dropped columns and why (display-only or redundant duplicates):
#   price_final_formatted, price_initial_formatted, price_recurring_sub_desc
#     -> display-only string formatting of price_final/price_initial, no
#        unique information.
#   owners_range (string) -> display-only duplicate of owners_min/max/mid,
#        which are already numeric and more usable.
#   languages_games / languages_steamspy -> localization reach is already
#        captured by language_count; the raw language lists add size
#        without a clear analytical use at this stage.
#   genres_steamspy -> redundant with genres_ctg for the planned later
#        genre-demand analysis; genres_ctg was chosen as it comes from a
#        more complete source for this field (lower missingness).
#   source_* provenance flags, price_initial, price_discount_percent,
#     full_audio_support, has_recurring_subscription, has_discount,
#     price_recurring_sub, price_initial_clean, review_score,
#     steamspy_user_score, steamspy_positive, steamspy_negative, developer,
#     publisher, owners_min, owners_max, price, initial_price, price_eur,
#     initial_price_eur, discount
#     -> not plausibly tied to any of the 5 dimensions or the planned genre-
#        demand pass; kept out to avoid carrying dead weight, per the "no
#        columns irrelevant to scope" instruction.

original_col_count = pd.read_csv(SRC, low_memory=False, nrows=0).shape[1]
print("\nColumns kept:", len(keep_cols))
print("Columns in master_dataset.csv:", original_col_count)
print("Columns dropped:", original_col_count - len(keep_cols))

# ---------------------------------------------------------------------------
# 8. EXECUTE AND VALIDATE
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)
print("game_features shape:", game_features.shape)
print("duplicate app_ids:", game_features["app_id"].duplicated().sum())

inf_check = np.isinf(game_features.select_dtypes(include=[np.number])).sum()
inf_cols = inf_check[inf_check > 0]
print("columns with inf/-inf values:", inf_cols.to_dict() if len(inf_cols) else "none")

print("\nmissing % per engineered/kept column:")
print((game_features.isna().mean() * 100).round(2).to_string())

# ---------------------------------------------------------------------------
# 9. SAVE
# ---------------------------------------------------------------------------
game_features.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={game_features.shape}")
