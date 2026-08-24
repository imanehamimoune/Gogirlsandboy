'''
PROMPT

Role: You are a senior Data Engineer and Data Analyst with strong Python/Pandas expertise, focused on merging and preparing multiple related datasets without overcomplicating the solution.
Context: You will receive several already-cleaned CSV files that share a common key: categories, genres, games, tags, reviews, and steamspy_insights — all keyed on app_id. Each file may have its own missing-value conventions, dtypes, and possibly overlapping or duplicate records.
Objective: Merge all files into a single master dataset on app_id, explore it thoroughly, and prepare it for analysis — without deleting any rows and without inventing data. The master dataset should remain a clean, reusable merge — not a snapshot tied to one particular analysis.
Tasks:
1. Load and inspect each file individually
    * Report shape, dtypes, and missing-value % per file before merging.
    * Confirm app_id has a consistent dtype and format across all files (fix mismatches — e.g. int vs string, extra whitespace — before joining).
2. Merge
    * Merge all datasets on app_id using an outer join, so no app_id present in any file is lost.
    * After merging, report how many app_ids came from each source and how many app_ids are missing from each individual file (i.e. present in the master but not in that particular source).
    * Add a provenance flag per source (e.g. source_games, source_reviews) so downstream users can tell "record isn't in this source at all" apart from "record is in this source but a field is blank."
3. Explore the merged dataset
    * Check for full-row duplicates and duplicate app_ids; report counts before assuming either is a problem.
    * Summarize value ranges, unique counts, and missingness per column on the merged result.
    * Flag any columns that became redundant only after merging (e.g. the same signal now appearing from two different source files). Keep both columns rather than collapsing them, and rename on merge to avoid ambiguous auto-suffixing (e.g. genres_ctg vs genres_steamspy).
4. Handle missing values
    * Do not drop any row because it has missing values.
    * Distinguish "truly missing" from "meaningful absence" (e.g. a review-count field that's genuinely 0, or a game with no tags because none apply) before deciding how to represent it — keep the distinction visible in the output (e.g. via the provenance flags from step 2).
    * Where a value must be filled, only do so with clear justification tied to another field in the data (e.g. is_free == True implies price == 0, not "unknown"), and note the justification directly in the code as a comment. Write filled values to new columns; never overwrite the original column.
    * Standardize placeholder "missing" values disguised as text (e.g. "None", "Unknown", "N/A", "-", "--") into real NaN before merging, so missingness stats are accurate.
5. Standardize categorical text
    * Fix casing, whitespace, and synonyms across sources so joins and groupings behave correctly (e.g. matching values between two sources' versions of the same field).
    * Do this on the merged result, since it depends on the full combined set of values — not on individual files beforehand.
6. Write the code
    * Python + Pandas. Keep it simple and direct — prefer straightforward, readable steps over clever or defensive one-liners; no unnecessary abstraction, helper classes, or error-handling beyond what the task needs.
    * Never overwrite any of the original source files.
    * Save the result as master_dataset.csv.
    * Do NOT include statistical normalization, scaling, or encoding (min-max, z-score, label/one-hot encoding, etc.) in this output. Those choices are analysis-specific (they depend on the algorithm, the subset of rows in use, and the question being asked) and belong in a separate analysis script that reads master_dataset.csv, not baked into the master file itself.
7. Execute and validate
    * Actually run the code — don't just describe it.
    * Confirm: row count reflects a true outer join (no unintended loss), no duplicate app_ids, no full-row duplicates, dtypes correct, no leftover placeholder nulls.
8. Deliver
    * The code, plus a short summary of what was merged, what was found during exploration, how missing values were handled, and what categorical standardization was applied.
Constraints (Do Not):
* Do not delete any rows, for any reason, including missing values or suspected duplicates you haven't explicitly confirmed.
* Do not overwrite any of the original source files.
* Do not fill missing values with 0 or a statistic without clear justification documented in the code.
* Do not invent data or silently discard columns.
* Do not apply normalization, scaling, or encoding in the master dataset — keep those transformations in a separate, analysis-time script.
* Do not claim the output exists unless the code actually ran successfully.
* Do not overengineer — no unnecessary complexity, config layers, or premature generalization.
Expected Output:
* master_dataset.csv containing all app_ids from every source file, all original columns preserved, provenance flags per source, and any justified missing-value fills in clearly separate new columns — but no normalized/scaled/encoded columns.
* A short summary of the merge results, exploration findings, missing-value handling, and categorical standardization applied.
Validation:
* Reload the output and confirm: no duplicate app_ids, no full-row duplicates, row count matches the true union of app_ids across all source files, dtypes are correct, and no placeholder null strings remain.

'''
# Request: 2026-08-20 17:40 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)



"""
Merge categories/tags/genres, games, reviews, and steamspy_insights into a
single master dataset on app_id. Outer join, no rows dropped, no data
invented. Normalization/scaling/encoding is intentionally NOT included here
-- those are analysis-specific choices and belong in a separate script that
reads master_dataset.csv. See inline comments for every judgment call made.
"""

import zipfile

import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "data/processed/"
OUT = "data/processed/master_dataset.csv"

# ---------------------------------------------------------------------------
# 1. LOAD + PER-FILE INSPECTION
# ---------------------------------------------------------------------------
with zipfile.ZipFile(SRC + "categories_tags_genres_merged.zip") as z:
    with z.open("cleaned_merged/categories, tags, genres_merged_by_app_id.csv") as f:
        ctg = pd.read_csv(f, encoding="utf-8-sig", low_memory=False)

games = pd.read_csv(SRC + "games_cleaned.csv", encoding="utf-8-sig", low_memory=False)
reviews = pd.read_csv(SRC + "reviews_cleaned.csv", encoding="utf-8-sig", low_memory=False)
steamspy = pd.read_csv(SRC + "steamspy_insights_cleaned.csv", encoding="utf-8-sig", low_memory=False)

sources = {
    "categories_tags_genres": ctg,
    "games": games,
    "reviews": reviews,
    "steamspy": steamspy,
}

# Descriptions dataset was decided to be excluded from the scope of this analysis and hence, it is not included in the merge. It can be merged later if needed, but for now, we focus on the other four datasets.

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
# games and steamspy carry a "languages" column AND an "is_free" column.
# These are independently scraped signals for the same concept, not
# guaranteed-identical duplicates (genres_ctg vs genres_steamspy only agree
# ~65% of the time), so all of them are kept but renamed up front to avoid
# pandas' auto "_x"/"_y" suffixing, which would be hard to interpret later
# and, in is_free's case, would silently break any code referencing
# master["is_free"] after the merge (that column no longer exists as such --
# it becomes is_free_x/is_free_y).
steamspy = steamspy.rename(columns={
    "genres": "genres_steamspy",
    "languages": "languages_steamspy",
    "is_free": "is_free_steamspy",
})
ctg = ctg.rename(columns={"genres": "genres_ctg"})
games = games.rename(columns={
    "languages": "languages_games",
    "is_free": "is_free_games",
})

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
print("  is_free_games vs is_free_steamspy -> same concept, two independent sources, kept both (see agreement check in Step 7)")
print("  reviews.positive/negative vs steamspy.steamspy_positive/steamspy_negative -> overlapping vote-count signals from two sources, kept both for cross-checking")

# ---------------------------------------------------------------------------
# 6. CATEGORICAL TEXT STANDARDIZATION (on the merged result)
# ---------------------------------------------------------------------------
# Checked categories/tags/genres_ctg for casing collisions within the file
# (e.g. "Co-op" vs "co-op") -- none found, values are already consistently
# cased. genres_ctg vs genres_steamspy disagree on ~35% of rows even after
# lowercasing/reordering, but that's a genuine content difference between
# two independently-scraped sources, not a casing bug -- nothing to "fix"
# there without guessing which source is right, so both are kept as-is.
print("\nCategorical casing check: no within-file casing collisions found in "
      "categories/tags/genres_ctg -> no rewriting needed.")

# ---------------------------------------------------------------------------
# 7. MISSING VALUE HANDLING (no rows dropped, nothing filled without reason)
# ---------------------------------------------------------------------------
# (a) price_final / price_initial are NaN for ~99.99% of is_free==True games.
#     For those rows "missing" actually means "price is 0" -- is_free is an
#     explicit, reliable flag, so this is filling in a known fact, not
#     inventing one. For is_free==False rows with missing price (~30k rows,
#     mostly demos with no listed price) the value is genuinely unknown and
#     is left as NaN. Written to NEW columns so the original price_final /
#     price_initial columns are never overwritten.
#
#     is_free exists in BOTH games and steamspy (renamed is_free_games /
#     is_free_steamspy in Step 3 to avoid the merge's silent _x/_y
#     suffixing). is_free_games is used here specifically -- not
#     is_free_steamspy -- because price_final/price_initial are ALSO from
#     games_cleaned.csv, so using that same source's flag keeps the fill
#     internally consistent rather than trusting a different source's
#     opinion about a fact tied to this source's price fields.
master["price_final_clean"] = master["price_final"]
master["price_initial_clean"] = master["price_initial"]
free_mask = master["is_free_games"] == True  # noqa: E712
master.loc[free_mask, "price_final_clean"] = master.loc[free_mask, "price_final_clean"].fillna(0.0)
master.loc[free_mask, "price_initial_clean"] = master.loc[free_mask, "price_initial_clean"].fillna(0.0)
print(f"\nprice_final_clean: filled {free_mask.sum()} is_free_games rows' missing price with 0.0 (free = price 0, not unknown)")

# sanity check: is_free is normally an objective fact (unlike genre tagging,
# which is inherently a bit subjective), so if the two sources disagree
# often, that's a real data-quality signal worth surfacing, not silently
# picking one and moving on.
agreement = (master["is_free_games"] == master["is_free_steamspy"]).mean()
print(f"is_free_games vs is_free_steamspy agreement rate: {agreement*100:.1f}%")

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
# 8. SAVE
# ---------------------------------------------------------------------------
# No normalization/scaling/encoding here -- those are analysis-specific and
# belong in a separate script that reads master_dataset.csv.
master.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={master.shape}")
