# ===== 1. IMPORTS =====

import pandas as pd
from bs4 import BeautifulSoup

# ==== 2. CONFIGURATION =====

FILE_PATH = "data/raw/descriptions.zip"
TEXT_COLUMNS = ["summary", "extensive", "about"]

# ==== 3. FUNCTIONS =====

def remove_html(text):
    """Remove HTML tags from a text value."""
    if pd.isna(text):
        return text

    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)

def data_quality_report(df, text_columns):
    """Print basic data-quality information."""

    print("\n" + "=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)

    # Basic information
    print("\n--- Basic Information ---")
    print(f"Shape: {df.shape}")

    print("\nData types:")
    print(df.dtypes)

    # Missing values
    print("\n--- Missing Values ---")
    print(df.isna().sum())

    # Duplicates
    print("\n--- Duplicates ---")
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(f"Duplicate app IDs: {df['app_id'].duplicated().sum()}")

    # Empty strings
    print("\n--- Empty Values ---")
    for col in text_columns:
        empty_count = df[col].fillna("").str.strip().eq("").sum()
        print(f"{col}: {empty_count}")

    # HTML
    print("\n--- HTML Detection ---")
    for col in text_columns:
        contains_html = (
            df[col]
            .fillna("")
            .str.contains(r"<[^>]+>", regex=True)
        )

        print(f"{col}: {contains_html.sum()} rows contain HTML")

    # Description lengths
    print("\n--- Description Lengths ---")
    for col in text_columns:
        lengths = df[col].fillna("").str.len()

        print(f"\n{col}:")
        print(lengths.describe())

    # Very short descriptions
    print("\n--- Very Short Descriptions (<20 characters) ---")

    for col in text_columns:
        short = df[df[col].notna() & (df[col].str.len() < 20)]

        print(f"\n{col}: {len(short)}")
        print(short[["app_id", col]].head(10))

# ===== 4. LOAD RAW DATA =====

df = pd.read_csv(FILE_PATH, escapechar="\\")

print(f"Loaded {len(df):,} rows.")

# # ===== 5. DATA QUALITY REPORT =====

# data_quality_report(df, TEXT_COLUMNS)

# for col in TEXT_COLUMNS:
#     short = df_processed.loc[
#         df_processed[col].notna() & (df_processed[col].str.len() < 20),
#         col
#     ]

#     print(f"\n--- {col} ---")
#     print(short.value_counts().head(20))

# # ===== 6. PROCESS DATA =====

df_processed = df.copy()

for col in TEXT_COLUMNS:
    print(f"Removing HTML from {col}...")
    df_processed[col] = df_processed[col].apply(remove_html)

for col in TEXT_COLUMNS:
    df_processed = df_processed[df_processed[col].fillna("").str.strip().str.len() >= 20].copy()

# ===== 7. SAVE DATA INTO CSV =====

df_processed.to_csv(
    "data/processed/descriptions_cleaned.zip",
    index=False,
    compression={
        "method": "zip",
        "archive_name": "descriptions_cleaned.csv"
    }
)
