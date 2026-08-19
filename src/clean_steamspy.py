from __future__ import annotations
 
import re
 
import numpy as np
import pandas as pd
 
# ---------------------------------------------------------------- constants
 
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
