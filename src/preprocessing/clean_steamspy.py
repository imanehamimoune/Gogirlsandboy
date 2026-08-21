"""
## Role

You are a data analyst working with Python, pandas, and NumPy. Your task is to clean and standardize a raw SteamSpy dataset while preserving useful information and creating analysis-ready features.

## Context

The input is a raw SteamSpy CSV export containing information about Steam applications, including:

* `app_id`
* developer and publisher information
* ownership ranges
* current and initial prices
* discount information
* concurrent-user counts
* playtime statistics
* languages
* genres

The raw data contains several quality and consistency issues. Company names may contain inconsistent whitespace, capitalization, legal suffixes, descriptive suffixes, or multiple companies in one field. Ownership information is stored as textual ranges. Prices are stored in cents. Some numeric values may be invalid or missing, and some columns may contain no useful information.

The cleaned dataset should preserve one row per application while generating additional variables that can be used for grouping, analysis, and modelling.

## Objective

Create a Python data-cleaning pipeline that loads the raw SteamSpy dataset, standardizes important fields, resolves duplicate application IDs, engineers useful analytical features, identifies questionable values, and produces a report documenting the transformations performed.

The main cleaning function should return both the cleaned DataFrame and a dictionary containing data-quality and transformation statistics.

## Tasks

1. **Load the raw data**

   * Read the CSV file using pandas.
   * Handle escaped characters correctly.
   * Interpret `"N"` and empty strings as missing values.
   * Ensure `app_id` is loaded as an integer.

2. **Ensure application ID integrity**

   * Detect duplicated `app_id` values.
   * Keep the first occurrence of each duplicated application.
   * Record the number of removed duplicates.
   * Temporarily use `app_id` as the index and sort the dataset by it.

3. **Clean developer and publisher information**

   * Normalize whitespace in `developer` and `publisher`.
   * Convert empty strings to missing values.
   * Preserve the cleaned original company names for display.
   * Extract the primary company when multiple companies are listed.
   * Correctly handle commas that belong to legal company suffixes rather than treating them as company separators.
   * Count how many companies are listed in each field.
   * Create normalized company keys for grouping and matching.
   * Normalize casing and repeatedly remove legal suffixes such as `Inc`, `Ltd`, `LLC`, `GmbH`, and similar forms.
   * Remove one descriptive suffix such as `Games`, `Studios`, `Interactive`, `Entertainment`, or `Software`.
   * Record missing and multi-company values.
   * Compare normalized developer and publisher keys to create a `self_published` indicator.

4. **Parse ownership ranges**

   * Convert textual ranges such as `"20,000 .. 50,000"` into numeric lower and upper bounds.
   * Calculate the midpoint of each ownership range.
   * Create a log-transformed ownership midpoint using `log1p`.
   * Create an ordered categorical ownership bucket based on the numeric lower bounds.
   * Record how many ownership ranges could not be parsed.

5. **Process prices and discounts**

   * Convert `price` and `initial_price` from cents to euros.
   * Convert the reported discount to a numeric percentage.
   * Identify free applications.
   * Detect cases where the current price exceeds the initial price.
   * Create a flag for these inconsistent prices.
   * Calculate the implied discount percentage from current and initial prices.
   * Flag unusually high initial prices above €200 as potential outliers.
   * Record the number of missing prices and inconsistent price records.

6. **Process usage and playtime fields**

   * Convert `concurrent_users_yesterday` to a nullable integer.
   * Replace negative concurrent-user values with missing values.
   * Record how many applications have non-zero concurrent users.
   * Check the predefined playtime columns.
   * Drop playtime columns if all their values are effectively zero.
   * Record which uninformative columns were removed.

7. **Create compact language and genre features**

   * Count the number of comma-separated languages listed for each application.
   * Count the number of comma-separated genres.
   * Store these as nullable integer features.

8. **Create a derived business metric**

   * Estimate gross revenue using:

     `owners_mid × price_eur`

   * Store the result as `est_revenue_eur`.

   * Treat this strictly as a proxy rather than actual revenue.

9. **Create a completeness indicator**

   * Create an `is_investable` flag.
   * Mark a row as investable only when publisher, price, and ownership midpoint information are available.
   * Record the number of investable rows.

10. **Produce a cleaning report**

    * Maintain a dictionary containing important processing statistics, including:

      * input row count
      * duplicate application IDs removed
      * missing developer and publisher counts
      * multi-company developer and publisher counts
      * unique raw and normalized publisher counts
      * unparsed ownership ranges
      * missing prices
      * inconsistent prices
      * non-zero concurrent-user counts
      * dropped uninformative columns
      * investable rows
      * output row count

11. **Return the results**

    * Reset the DataFrame index.
    * Return the cleaned DataFrame and the report dictionary.
    * When the script is executed directly, print the report and the resulting column data types.

## Constraints

* Use Python with `pandas`, `numpy`, and `re`.
* Keep `app_id` as the unique identifier.
* Do not drop rows because individual analytical fields are missing.
* Only duplicate `app_id` records may be removed.
* Preserve readable developer and publisher names separately from normalized grouping keys.
* Company-name normalization must be used for matching and grouping, not as a replacement for the display values.
* Legal suffix removal must account for stacked suffixes.
* Do not incorrectly split legal names such as `"CINEMAX, s.r.o."` into separate companies.
* Use pandas nullable data types where appropriate.
* Invalid numeric values should be converted to missing values rather than causing the pipeline to fail.
* Only drop playtime columns when they contain no useful variation.
* Do not present `est_revenue_eur` as true revenue because ownership ranges are approximate and the calculation ignores factors such as regional pricing, refunds, platform fees, bundles, and free-to-play monetization.
* Keep the implementation modular by using helper functions for repeated or logically separate transformations.

## Expected Output

Provide a complete Python script containing:

* required imports
* configuration constants
* a raw-data loading function
* company-name normalization helpers
* company extraction and counting helpers
* an ownership-range parsing helper
* a cents-to-euros conversion helper
* a comma-separated item-count helper
* a main `clean_steamspy(path)` function
* a script entry point for running the pipeline directly

The `clean_steamspy(path)` function should return:

```python
cleaned_df, report
```

where:

* `cleaned_df` is the cleaned and feature-engineered SteamSpy DataFrame.
* `report` is a dictionary summarizing the major cleaning operations and data-quality findings.

## Validation

Verify that the completed pipeline satisfies the following conditions:

1. `app_id` is unique in the final DataFrame.
2. Duplicate `app_id` records are counted before removal.
3. Missing values are handled without unintentionally dropping rows.
4. Empty developer and publisher strings are converted to missing values.
5. Original readable company names remain available after normalization.
6. Legal company suffixes do not create false multi-company records.
7. Normalized company keys consistently handle casing, whitespace, and company suffixes.
8. The `self_published` flag is only true when both normalized company keys exist and match.
9. Ownership ranges are correctly converted into lower, upper, midpoint, log-midpoint, and ordered bucket features.
10. Prices are correctly converted from cents to euros.
11. Free applications are correctly identified.
12. Current prices greater than initial prices are flagged.
13. Implied discount percentages are calculated only when the initial price is greater than zero.
14. Negative concurrent-user values are converted to missing values.
15. Playtime columns are removed only when they contain no meaningful information.
16. Language and genre counts are missing-value safe.
17. The estimated revenue feature uses ownership midpoint multiplied by current price.
18. `is_investable` requires publisher, price, and ownership information.
19. The report accurately reflects the transformations performed.
20. The final output contains one row per unique `app_id` and returns both the cleaned DataFrame and the report dictionary.
"""
# Request: 2026-08-19 18:18 CET.
# Author: Imane Hamimoune (prompt and adjustments), ChatGPT (code)

from __future__ import annotations
 
import re
 
import numpy as np
import pandas as pd
 

 
RAW_DTYPES = {"app_id": "int64"}
 
CENT_COLUMNS = ["price", "initial_price"]
PLAYTIME_COLUMNS = [
    "playtime_average_forever",
    "playtime_average_2weeks",
    "playtime_median_forever",
    "playtime_median_2weeks",
]
 
# Legal-form suffixes. Stripped repeatedly, because they stack:
# "Capcom Co., Ltd." -> "capcom co" -> "capcom".
LEGAL_SUFFIX = (
    r",?\s+(inc|ltd|limited|llc|llp|gmbh|ug|ag|ab|a\.?s|bv|b\.?v|s\.?r\.?o|srl|"
    r"s\.?a|sas|s\.?l|oy|pte|k\.?k|d\.?o\.?o|co|corp|corporation|company)\.?$"
)
 
# Descriptive words. Stripped once only -- stripping repeatedly would turn
# "Game Science" into "science".
DESCRIPTIVE_SUFFIX = r",?\s+(studios?|games?|interactive|entertainment|publishing|productions?|media|digital|software)\.?$"
 
 

 
 
def load_raw(path: str) -> pd.DataFrame:
    """Read the raw export with the two MySQL quirks handled."""
    return pd.read_csv(
        path,
        escapechar="\\",
        na_values=["N", ""],
        keep_default_na=True,
        dtype=RAW_DTYPES,
    )
 
 
 
 
def _normalise_company(s: pd.Series) -> pd.Series:
    """Whitespace/casing/legal-suffix normalisation for grouping only.
 
    Returns a *join key*, not a display name. Keep the original column for
    anything the client will read.
    """
    out = (
        s.astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.casefold()
    )
    # Legal forms stack, so loop until stable (bounded to avoid pathological input).
    for _ in range(3):
        stripped = out.str.replace(LEGAL_SUFFIX, "", regex=True).str.strip(" .,-")
        if stripped.equals(out):
            break
        out = stripped
    out = out.str.replace(DESCRIPTIVE_SUFFIX, "", regex=True).str.strip(" .,-")
    return out.replace("", pd.NA)
 
 
 
# Fragments that are a legal suffix rather than a separate company. Used to
# avoid splitting "CINEMAX, s.r.o." into two publishers.
_SUFFIX_FRAGMENT = re.compile(
    r"^\s*(inc|ltd|limited|llc|llp|gmbh|ab|a\.?s|bv|b\.?v|s\.?r\.?o|srl|s\.?a|sas|oy|pte|co|corp|corporation|company)\.?\s*$",
    re.IGNORECASE,
)
 
 
def _primary_company(value) -> object:
    """First company in a comma-separated publisher/developer field.
 
    5.6% of publisher fields list several companies ("Frontier, Aspyr (Mac)"),
    but commas are also used inside legal names ("CINEMAX, s.r.o."), so a bare
    ``split(',')[0]`` truncates real names. Fragments matching a legal suffix
    are folded back into the preceding one.
    """
    if pd.isna(value):
        return pd.NA
    parts = [p.strip() for p in str(value).split(",") if p.strip()]
    if not parts:
        return pd.NA
    primary = parts[0]
    for frag in parts[1:]:
        if _SUFFIX_FRAGMENT.match(frag):
            primary = f"{primary}, {frag}"
        else:
            break
    return primary
 
 
def _n_companies(value) -> object:
    """How many distinct companies the field lists (suffix commas ignored)."""
    if pd.isna(value):
        return pd.NA
    parts = [p.strip() for p in str(value).split(",") if p.strip()]
    return sum(1 for p in parts if not _SUFFIX_FRAGMENT.match(p)) or 1
 
 
def _parse_owners(s: pd.Series) -> pd.DataFrame:
    """Turn '20,000 .. 50,000' into numeric low / high / midpoint columns."""
    cleaned = s.astype("string").str.replace(",", "", regex=False)
    parts = cleaned.str.split(r"\s*\.\.\s*", n=1, regex=True, expand=True)
 
    low = pd.to_numeric(parts[0], errors="coerce")
    high = pd.to_numeric(parts[1], errors="coerce") if parts.shape[1] > 1 else pd.Series(np.nan, index=s.index)
 
    mid = (low + high) / 2
    return pd.DataFrame(
        {
            "owners_low": low,
            "owners_high": high,
            "owners_mid": mid,
            # log1p because the distribution spans five orders of magnitude
            # and 83% of titles sit in the bottom bucket.
            "owners_mid_log": np.log1p(mid),
        },
        index=s.index,
    )
 
 
def _cents_to_eur(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce") / 100.0
 
 
def _split_count(s: pd.Series) -> pd.Series:
    """Count comma-separated items, NA-safe."""
    return (
        s.astype("string")
        .str.split(",")
        .apply(lambda x: len([i for i in x if i.strip()]) if isinstance(x, list) else pd.NA)
        .astype("Int64")
    )
 
 
# ---------------------------------------------------------------- main
 
 
def clean_steamspy(path: str) -> tuple[pd.DataFrame, dict]:
    """Clean and standardise steamspy_insights.csv.
 
    Returns
    -------
    df : cleaned DataFrame, one row per app_id, nothing dropped
    report : dict of counts for documentation
    """
    df = load_raw(path)
    report: dict[str, object] = {"rows_in": len(df)}
 
    # --- 1. key integrity -------------------------------------------------
    dupes = int(df["app_id"].duplicated().sum())
    report["duplicate_app_ids_removed"] = dupes
    if dupes:
        df = df.drop_duplicates(subset="app_id", keep="first")
    df = df.set_index("app_id", drop=False).sort_index()
 
    # --- 2. company names -------------------------------------------------
    for col in ["developer", "publisher"]:
        df[col] = df[col].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
        df[col] = df[col].replace("", pd.NA)
 
        # Some fields list several companies. Keep the raw string for display,
        # extract the first for grouping, and record how many were listed.
        df[f"{col}_primary"] = df[col].apply(_primary_company).astype("string")
        df[f"n_{col}s"] = df[col].apply(_n_companies).astype("Int64")
        df[f"{col}_key"] = _normalise_company(df[f"{col}_primary"])
 
        report[f"{col}_missing"] = int(df[col].isna().sum())
        report[f"{col}_multi_company"] = int(df[f"n_{col}s"].gt(1).sum())
 
    report["publisher_raw_nunique"] = int(df["publisher"].nunique())
    report["publisher_key_nunique"] = int(df["publisher_key"].nunique())
    df["self_published"] = (
        df["developer_key"].notna()
        & df["publisher_key"].notna()
        & (df["developer_key"] == df["publisher_key"])
    )
 
    # --- 3. owners bucket -------------------------------------------------
    df = df.join(_parse_owners(df["owners_range"]))
    report["owners_unparsed"] = int(df["owners_mid"].isna().sum())
    # ordinal rank of the bucket, useful as a model feature
    df["owners_bucket"] = pd.Categorical(
        df["owners_range"],
        categories=(
            df.groupby("owners_range", observed=True)["owners_low"].first().sort_values().index.tolist()
        ),
        ordered=True,
    )
 
    # --- 4. prices --------------------------------------------------------
    for col in CENT_COLUMNS:
        df[f"{col}_eur"] = _cents_to_eur(df[col])
    df["discount_pct"] = pd.to_numeric(df["discount"], errors="coerce")
 
    report["price_missing"] = int(df["price_eur"].isna().sum())
    df["is_free"] = df["price_eur"].eq(0)
 
    # Consistency check: discounted price should not exceed list price.
    bad_price = (
        df["price_eur"].notna()
        & df["initial_price_eur"].notna()
        & (df["price_eur"] > df["initial_price_eur"])
    )
    report["price_above_initial"] = int(bad_price.sum())
    df["flag_price_inconsistent"] = bad_price
 
    # Implied discount vs reported discount.
    implied = np.where(
        df["initial_price_eur"].gt(0),
        (1 - df["price_eur"] / df["initial_price_eur"]) * 100,
        np.nan,
    )
    df["discount_implied_pct"] = np.round(implied, 1)
 
    # Absurd prices (placeholder junk sits at the top of the distribution).
    df["flag_price_outlier"] = df["initial_price_eur"] > 200
 
    # --- 5. counts --------------------------------------------------------
    df["concurrent_users_yesterday"] = pd.to_numeric(
        df["concurrent_users_yesterday"], errors="coerce"
    ).astype("Int64")
    df.loc[df["concurrent_users_yesterday"].lt(0), "concurrent_users_yesterday"] = pd.NA
    report["ccu_nonzero"] = int(df["concurrent_users_yesterday"].gt(0).sum())
 
    # All four playtime columns are 0 in every row of this export -- the
    # scrape did not populate them. They carry zero information, so drop
    # them rather than silently feeding a constant into a model.
    dead = [c for c in PLAYTIME_COLUMNS if pd.to_numeric(df[c], errors="coerce").fillna(0).abs().max() == 0]
    report["dead_columns_dropped"] = dead
    df = df.drop(columns=dead)
 
    # --- 6. redundant text columns ---------------------------------------
    # languages/genres also exist in games.csv and genres.csv. Keep only a
    # cheap count here and let the dedicated tables be authoritative.
    df["n_languages_spy"] = _split_count(df["languages"])
    df["n_genres_spy"] = _split_count(df["genres"])
 
    # --- 7. derived business metric --------------------------------------
    # Proxy only: no true revenue exists in this dataset. Wide owner buckets,
    # ignores regional pricing, refunds, Steam's cut, bundles and F2P.
    df["est_revenue_eur"] = df["owners_mid"] * df["price_eur"]
 
    # --- 8. completeness flag --------------------------------------------
    df["is_investable"] = (
        df["publisher"].notna() & df["price_eur"].notna() & df["owners_mid"].notna()
    )
    report["investable_rows"] = int(df["is_investable"].sum())
    report["rows_out"] = len(df)
 
    return df.reset_index(drop=True), report
 
 
if __name__ == "__main__":
    import sys
 
    src = sys.argv[1] if len(sys.argv) > 1 else "data/raw/steamspy_insights.csv"
    frame, rep = clean_steamspy(src)
    for k, v in rep.items():
        print(f"{k:<28} {v}")
    print()
    print(frame.dtypes)
