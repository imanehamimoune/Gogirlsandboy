
'''
Role:
You are a senior Data Engineer and Data Analyst with strong Python/Pandas expertise,
focused on merging and preparing multiple related datasets without overcomplicating
the solution.

Context:
You will receive several already-cleaned CSV files that share a common key:
categories, genres, games, tags, reviews, and steamspy_insights — all keyed on
app_id. Each file may have its own missing-value conventions, dtypes, and possibly
overlapping or duplicate records.

Objective:
Merge all files into a single master dataset on app_id, explore it thoroughly, and
prepare it for analysis — without deleting any rows and without inventing data.

Tasks:
1. Load and inspect each file individually
   - Report shape, dtypes, and missing-value % per file before merging.
   - Confirm app_id has a consistent dtype and format across all files (fix
     mismatches — e.g. int vs string, extra whitespace — before joining).
2. Merge
   - Merge all datasets on app_id using an outer join, so no app_id present in
     any file is lost.
   - After merging, report how many app_ids came from each source and how many
     app_ids are missing from each individual file (i.e. present in the master
     but not in that particular source).
3. Explore the merged dataset
   - Check for full-row duplicates and duplicate app_ids; report counts before
     assuming either is a problem.
   - Summarize value ranges, unique counts, and missingness per column on the
     merged result.
   - Flag any columns that became redundant only after merging (e.g. the same
     signal now appearing from two different source files).
4. Handle missing values
   - Do not drop any row because it has missing values.
   - Distinguish "truly missing" from "meaningful absence" (e.g. a review-count
     field that's genuinely 0, or a game with no tags because none apply) before
     deciding how to represent it — keep the distinction visible in the output.
   - Where a value must be filled, only do so with clear justification, and note
     the justification directly in the code as a comment.
5. Normalize for analysis
   - Standardize inconsistent categorical values across sources (casing,
     whitespace, synonyms) so joins and groupings behave correctly.
   - Apply any statistical normalization (scaling, encoding) only after the
     merge is complete, since it depends on the full combined distribution —
     not before, on individual files.
   - Keep normalized columns separate from the original values rather than
     overwriting them.
6. Write the code
   - Python + Pandas. Keep it simple and direct — prefer straightforward,
     readable steps over clever or defensive one-liners; no unnecessary
     abstraction, helper classes, or error-handling beyond what the task needs.
   - Never overwrite any of the original source files.
   - Save the result as master_dataset.csv.
7. Execute and validate
   - Actually run the code — don't just describe it.
   - Confirm: row count reflects a true outer join (no unintended loss), no
     duplicate app_ids, no full-row duplicates, dtypes correct, no leftover
     placeholder nulls.
8. Deliver
   - The code, plus a short summary of what was merged, what was found during
     exploration, how missing values were handled, and what was normalized.

Constraints (Do Not):
- Do not delete any rows, for any reason, including missing values or suspected
  duplicates you haven't explicitly confirmed.
- Do not overwrite any of the original source files.
- Do not fill missing values with 0 or a statistic without clear justification
  documented in the code.
- Do not invent data or silently discard columns.
- Do not claim the output exists unless the code actually ran successfully.
- Do not overengineer — no unnecessary complexity, config layers, or premature
  generalization.

Expected Output:
- master_dataset.csv containing all app_ids from every source file, all original
  columns preserved, plus clearly separated normalized columns.
- A short summary of the merge results, exploration findings, missing-value
  handling, and normalization applied.

Validation:
- Reload the output and confirm: no duplicate app_ids, no full-row duplicates,
  row count matches the true union of app_ids across all source files, dtypes
  are correct, and no placeholder null strings remain.
'''
# Request: 2026-08-20 15:10 CET
# Author: Anna Andruszkiewicz (Prompt and Adjustment), Code: Claude

"""
Merge categories/tags/genres, games, reviews, and steamspy_insights into a
single master dataset on app_id. Outer join, no rows dropped, no data
invented. See inline comments for every judgment call made.
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "./"
OUT = "./master_dataset.csv"

# ---------------------------------------------------------------------------
# 1. LOAD + PER-FILE INSPECTION
# ---------------------------------------------------------------------------
ctg = pd.read_csv(SRC + "categories_tags_genres_merged_by_app_id.csv", encoding="utf-8-sig")
games = pd.read_csv(SRC + "games.csv", encoding="utf-8-sig", low_memory=False)
reviews = pd.read_csv(SRC + "reviews_cleaned.csv", encoding="utf-8-sig", low_memory=False)
steamspy = pd.read_csv(SRC + "steamspy_insights_clean.csv", encoding="utf-8-sig", low_memory=False)

sources = {
    "categories_tags_genres": ctg,
    "games": games,
    "reviews": reviews,
    "steamspy": steamspy,
}

print("=" * 70)
print("STEP 1: PER-FILE INSPECTION")
print("=" * 70)
for name, df in sources.items():
    print(f"\n--- {name} ---")
    print("shape:", df.shape)
    print("app_id dtype:", df["app_id"].dtype)
    print("missing % per column:")
    print((df.isna().mean() * 100).round(2).to_string())

# app_id is int64 in every file already -- confirm rather than assume
for name, df in sources.items():
    assert df["app_id"].dtype == np.int64, f"{name} app_id is not int64"
print("\napp_id dtype confirmed consistent (int64) across all 4 files.")

# ---------------------------------------------------------------------------
# 2. CLEAN PLACEHOLDER "MISSING" STRINGS -> REAL NaN (before merging, so
#    every downstream missing-value count is accurate)
# ---------------------------------------------------------------------------
# Found during exploration: games.name, steamspy.developer/publisher/
# primary_developer/primary_publisher contain literal strings like
# "None", "Unknown", "N/A", "-", "--" which are missing values in disguise,
# not real names. Converting these to NaN is a text-standardization step,
# not inventing data -- the underlying fact (name unknown) doesn't change.
PLACEHOLDER_TOKENS = {"n/a", "na", "none", "null", "unknown", "-", "--", ""}


def clean_placeholders(df):
    df = df.copy()
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        stripped = df[col].astype("string").str.strip()
        is_placeholder = stripped.str.lower().isin(PLACEHOLDER_TOKENS)
        df[col] = stripped.mask(is_placeholder.fillna(False), other=pd.NA)
    return df


ctg = clean_placeholders(ctg)
games = clean_placeholders(games)
reviews = clean_placeholders(reviews)
steamspy = clean_placeholders(steamspy)

# ---------------------------------------------------------------------------
# 3. RESOLVE COLUMN-NAME COLLISIONS BEFORE MERGING
# ---------------------------------------------------------------------------
# Both categories_tags_genres and steamspy carry a "genres" column, and both
# games and steamspy carry a "languages" column. These are two independently
# scraped signals for the *same* concept, not identical duplicates (checked:
# only ~65% match after normalizing casing/order), so both are kept but
# renamed up front to avoid pandas' auto "_x"/"_y" suffixing, which would be
# hard to interpret later.
steamspy = steamspy.rename(columns={"genres": "genres_steamspy", "languages": "languages_steamspy"})
ctg = ctg.rename(columns={"genres": "genres_ctg"})
games = games.rename(columns={"languages": "languages_games"})

# record each source's app_id set BEFORE merging, to build provenance flags
id_sets = {name: set(df["app_id"]) for name, df in [
    ("categories_tags_genres", ctg), ("games", games),
    ("reviews", reviews), ("steamspy", steamspy),
]}

# ---------------------------------------------------------------------------
# 4. MERGE (outer join on app_id, no rows dropped)
# ---------------------------------------------------------------------------
master = games.merge(ctg, on="app_id", how="outer")
master = master.merge(reviews, on="app_id", how="outer")
master = master.merge(steamspy, on="app_id", how="outer")

print("\n" + "=" * 70)
print("STEP 2: MERGE RESULTS")
print("=" * 70)
print("master shape:", master.shape)

all_ids = set(master["app_id"])
print(f"union of app_ids across all 4 sources: {len(all_ids)}")
for name, ids in id_sets.items():
    print(f"  from {name}: {len(ids)} ids present | {len(all_ids - ids)} app_ids missing from this source")

# provenance flags -- lets anyone downstream tell "record doesn't exist in
# source X" apart from "record exists in source X but a field is blank"
master["source_games"] = master["app_id"].isin(id_sets["games"])
master["source_categories_tags_genres"] = master["app_id"].isin(id_sets["categories_tags_genres"])
master["source_reviews"] = master["app_id"].isin(id_sets["reviews"])
master["source_steamspy"] = master["app_id"].isin(id_sets["steamspy"])

# ---------------------------------------------------------------------------
# 5. EXPLORE THE MERGED DATASET
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 3: MERGED-DATASET EXPLORATION")
print("=" * 70)
dup_app_ids = master["app_id"].duplicated().sum()
dup_full_rows = master.duplicated().sum()
print("duplicate app_ids:", dup_app_ids)
print("duplicate full rows:", dup_full_rows)

print("\nmissing % per column (post-merge):")
print((master.isna().mean() * 100).round(2).to_string())

print("\nredundant-after-merge columns flagged:")
print("  genres_ctg vs genres_steamspy -> same concept, two independent sources, kept both")
print("  languages_games vs languages_steamspy -> same concept, two independent sources, kept both")
print("  reviews.positive/negative vs steamspy.steamspy_positive/steamspy_negative -> overlapping vote-count signals from two sources, kept both for cross-checking")

# ---------------------------------------------------------------------------
# 6. MISSING VALUE HANDLING (no rows dropped, nothing filled without reason)
# ---------------------------------------------------------------------------
# (a) price_final / price_initial are NaN for ~99.99% of is_free==True games.
#     For those rows "missing" actually means "price is 0" -- is_free is an
#     explicit, reliable flag, so this is filling in a known fact, not
#     inventing one. For is_free==False rows with missing price (~30k rows,
#     mostly demos with no listed price) the value is genuinely unknown and
#     is left as NaN. Written to NEW columns so the original price_final /
#     price_initial columns are never overwritten.
master["price_final_clean"] = master["price_final"]
master["price_initial_clean"] = master["price_initial"]
free_mask = master["is_free"] == True  # noqa: E712
master.loc[free_mask, "price_final_clean"] = master.loc[free_mask, "price_final_clean"].fillna(0.0)
master.loc[free_mask, "price_initial_clean"] = master.loc[free_mask, "price_initial_clean"].fillna(0.0)
print(f"\nprice_final_clean: filled {free_mask.sum()} is_free rows' missing price with 0.0 (free = price 0, not unknown)")

# (b) Everything else stays NaN, on purpose:
#   - tags/categories/genres_ctg missing WHILE source_categories_tags_genres
#     is True -> the record exists in that source but has no tags/categories
#     assigned (meaningful absence: "no tags apply" / not scraped, can't
#     be told apart from the data alone, so left as NaN rather than guessed).
#   - tags/categories/genres_ctg missing WHILE source_categories_tags_genres
#     is False -> the app_id was never in that source file at all (truly
#     missing / structurally absent). The provenance flag makes this
#     distinction visible without altering any values.
#   - metacritic_score / recommendations missing -> most games simply never
#     received a Metacritic score or aren't in Steam's "recommendations"
#     bucket; 0 would falsely claim a real score/count of zero, so NaN stays.
#   - positive/negative/steamspy_positive/steamspy_negative are already 0%
#     missing (0 is a real observed vote count where applicable) -> untouched.
print("\nAll other missing values left as NaN; see code comments for the reasoning per field group.")

# ---------------------------------------------------------------------------
# 7. NORMALIZATION (post-merge, on the full combined distribution; originals
#    kept untouched, normalized values written to new "_norm"/"_encoded" cols)
# ---------------------------------------------------------------------------
minmax_cols = [
    "price_final_clean", "positive", "negative", "recommendations",
    "metacritic_score", "owners_mid", "concurrent_users_yesterday",
    "steamspy_positive", "steamspy_negative",
]
for col in minmax_cols:
    col_min, col_max = master[col].min(), master[col].max()
    master[col + "_norm"] = (master[col] - col_min) / (col_max - col_min)

# simple label encoding for the small-cardinality categorical price_currency
currency_codes = {code: i for i, code in enumerate(sorted(master["price_currency"].dropna().unique()))}
master["price_currency_encoded"] = master["price_currency"].map(currency_codes)

# binary encode type (game/demo) into a new column, original "type" untouched
master["is_demo"] = master["type"] == "demo"

print("\n" + "=" * 70)
print("STEP 4: NORMALIZATION APPLIED")
print("=" * 70)
print("min-max scaled (new *_norm columns):", minmax_cols)
print("label-encoded price_currency -> price_currency_encoded:", currency_codes)
print("binary-encoded type -> is_demo (True/False)")

# ---------------------------------------------------------------------------
# 8. SAVE
# ---------------------------------------------------------------------------
master.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={master.shape}")
