'''# Master Prompt: Games CSV Cleaning and Transformation

Role:
You are a Data Engineer with strong Python/Pandas expertise, building a
deterministic, fully reproducible cleaning script for a raw games catalog.
The output must be exact and repeatable — no judgment calls, no
approximations, no additional transformations beyond what's specified.

Context:
Input is data/raw/games.zip — a raw games catalog with a JSON-encoded
price_overview column, an HTML-contaminated languages column, and several
fields needing typed conversion. This script is one fixed piece of a larger
pipeline; its paths, column names, and exact string/regex logic must not
be altered or reinterpreted.

Objective:
Produce a single, self-contained, directly executable script — assuming no
prior state from any other script — that reads data/raw/games.zip and
writes data/processed/games_cleaned.csv, applying exactly the 13
transformations below, in order, and nothing else.

Setup:
- Imports: pandas as pd, json, numpy as np, pathlib.Path (Path only to
  create the output directory if missing).
- INPUT_PATH = "data/raw/games.zip"
- OUTPUT_PATH = "data/processed/games_cleaned.csv"
- Load: df_raw = pd.read_csv(INPUT_PATH, escapechar='\\')

Tasks (exact order, exact logic):
1. Parse price_overview JSON. Define parse_price(x): return {} if x is NaN
   or '', else json.loads(x), catching JSONDecodeError/TypeError -> {}.
   Apply to df_raw['price_overview'] -> price_data.
2. Normalize: price_df = pd.json_normalize(price_data); prefix every
   resulting column with "price_".
3. Combine: df = pd.concat([df_raw.drop(columns='price_overview'),
   price_df], axis=1).
4. release_date: replace the literal string "N" with pd.NA, then convert
   with pd.to_datetime(df['release_date'], errors='coerce').
5. is_free: df["is_free"] = df["is_free"].astype(bool).
6. full_audio_support: df["languages"].str.contains(
   "languages with full audio support", case=False, na=False).
7. Clean languages, this exact chained sequence, in order:
   - .str.replace(r"<br\s*/?>.*$", "", regex=True)
   - .str.replace(r"<[^>]+>", "", regex=True)
   - .str.replace("*", "", regex=False)
   - .str.replace(r"\s+", " ", regex=True)
   - .str.strip()
   Then replace the literal string "N" with np.nan.
8. Drop rows where name is exactly equal to either of these two strings
   (verbatim, including the " 2" variant):
   - 'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM!'
   - 'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM! 2'
   via df = df[~df["name"].isin(names_to_drop)]. Remove no other rows.
9. EUR-only price columns. For exactly this list —
   ['price_final', 'price_initial', 'price_currency',
   'price_final_formatted', 'price_discount_percent',
   'price_initial_formatted', 'price_recurring_sub',
   'price_recurring_sub_desc'] — set all of them to np.nan wherever
   price_currency != 'EUR'. No currency conversion, no exchange-rate math,
   no inferring missing currencies.
10. has_recurring_subscription: df["price_recurring_sub"].notna().
11. has_discount: df["price_discount_percent"].notna() &
    (df["price_discount_percent"] != 0). Do not infer from other columns.
12. language_count: split cleaned languages on "," and count elements;
    return 0 where the value isn't a list (e.g. missing).
13. Save: create the output directory if it doesn't exist; write with
    df.to_csv(OUTPUT_PATH, index=False) — no pandas index column.

Constraints (Do Not):
- Do not remove, add, or rename any column beyond what's explicitly listed.
- Do not remove any rows beyond the two exact names in Task 8.
- Do not convert currencies, perform exchange-rate math, or infer missing
  currencies.
- Do not add feature engineering, imputation, scaling, or standardization
  beyond what's explicitly specified.
- Do not remove duplicates or sort the DataFrame.
- Do not change any dtype beyond the explicit conversions above.
- Do not deviate from the exact regexes, literal strings, or column lists
  given — they must be reproduced verbatim.
- Do not add print/logging/validation statements beyond the transformations
  themselves — this is a silent, deterministic pipeline step.
- Do not assume variables or state from any other script; the script must
  run standalone from the project root.

Expected Output:
One script (e.g. src/feature_engineering/clean_games.py), fully executable
as-is, with clear section comments per task, that reads data/raw/games.zip
and writes data/processed/games_cleaned.csv implementing Tasks 1-13 in
exact order and nothing beyond them.'''

# Request: 2026-08-19 20:50 CET.
# Author: Christian Beemelmann (prompt and adjustments), ChatGPT (code)

import pandas as pd
import json
import numpy as np
from pathlib import Path


# =============================================================================
# 1. CONFIGURATION
# =============================================================================

INPUT_PATH = "data/raw/games.zip"
OUTPUT_PATH = "data/processed/games_cleaned.csv"


# =============================================================================
# 2. LOAD RAW CSV
# =============================================================================

df_raw = pd.read_csv(
    INPUT_PATH,
    escapechar='\\'
)

# =============================================================================
# 3. PARSE PRICE JSON
# =============================================================================

def parse_price(x):
    if pd.isna(x) or x == '':
        return {}

    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}


price_data = df_raw['price_overview'].apply(parse_price)

# =============================================================================
# 4. NORMALIZE PRICE JSON DATA
# =============================================================================

price_df = pd.json_normalize(price_data)
price_df = price_df.add_prefix('price_')

# =============================================================================
# 5. COMBINE PRICE DATA WITH ORIGINAL DATASET
# =============================================================================

df = pd.concat(
    [df_raw.drop(columns='price_overview'), price_df],
    axis=1
)

# =============================================================================
# 6. CLEAN AND CONVERT RELEASE DATE
# =============================================================================

df['release_date'] = df['release_date'].replace('N', pd.NA)
df['release_date'] = pd.to_datetime(
    df['release_date'],
    errors='coerce'
)

# =============================================================================
# 7. CONVERT IS_FREE TO BOOLEAN
# =============================================================================

df["is_free"] = df["is_free"].astype(bool)

# =============================================================================
# 8. CREATE FULL_AUDIO_SUPPORT
# =============================================================================

df["full_audio_support"] = df["languages"].str.contains(
    "languages with full audio support",
    case=False,
    na=False
)

# =============================================================================
# 9. CLEAN LANGUAGES COLUMN
# =============================================================================

df["languages"] = (
    df["languages"]
    .str.replace(r"<br\s*/?>.*$", "", regex=True)
    .str.replace(r"<[^>]+>", "", regex=True)
    .str.replace("*", "", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

df["languages"] = df["languages"].replace("N", np.nan)

# =============================================================================
# 10. REMOVE TWO SPECIFIC INVALID GAME ENTRIES
# =============================================================================

names_to_drop = [
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM!',
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM! 2'
]

df = df[~df["name"].isin(names_to_drop)]

# =============================================================================
# 11. KEEP PRICE DATA ONLY FOR EUR
# =============================================================================

cols = [
    'price_final',
    'price_initial',
    'price_currency',
    'price_final_formatted',
    'price_discount_percent',
    'price_initial_formatted',
    'price_recurring_sub',
    'price_recurring_sub_desc',
]

df.loc[df['price_currency'] != 'EUR', cols] = np.nan

# =============================================================================
# 12. CREATE HAS_RECURRING_SUBSCRIPTION
# =============================================================================

df["has_recurring_subscription"] = df["price_recurring_sub"].notna()

# =============================================================================
# 13. CREATE HAS_DISCOUNT
# =============================================================================

df["has_discount"] = (
    df["price_discount_percent"].notna()
    & (df["price_discount_percent"] != 0)
)

# =============================================================================
# 14. CREATE LANGUAGE_COUNT
# =============================================================================

df["language_count"] = (
    df["languages"]
    .str.split(",")
    .apply(lambda x: len(x) if isinstance(x, list) else 0)
)

# =============================================================================
# 15. SAVE FINAL DATASET
# =============================================================================

Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)
