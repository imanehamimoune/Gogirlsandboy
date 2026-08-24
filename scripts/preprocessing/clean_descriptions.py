"""

PROMPT

## Role

You are a data analyst working with Python and pandas. Your responsibility is to assess the quality of a dataset before any cleaning or preprocessing is performed.

## Context

The dataset contains application descriptions and includes an `app_id` column together with several text columns. The text columns to inspect are provided through a `text_columns` parameter and may contain missing values, empty strings, HTML, or unusually short descriptions.

## Objective

Create a reusable Python function called `data_quality_report(df, text_columns)` that examines the DataFrame and prints a clear summary of potential data-quality issues without modifying the original data.

## Tasks

The function should perform the following checks:

1. Report the dataset shape and data type of each column.
2. Count missing (`NaN`) values for every column.
3. Count completely duplicated rows.
4. Count duplicated values in the `app_id` column.
5. For each column in `text_columns`, count values that are empty or contain only whitespace.
6. For each text column, detect and count rows containing HTML tags using a regular expression.
7. Calculate the character length of each text value and print descriptive statistics using `describe()`.
8. Identify non-missing descriptions shorter than 20 characters.
9. For each text column, print the number of very short descriptions and display the first 10 examples together with their `app_id`.

## Constraints

* Use Python and pandas.
* The function must be named `data_quality_report(df, text_columns)`.
* Do not modify the input DataFrame.
* Do not remove, replace, or clean any values.
* Treat missing values as empty strings only when checking for empty values, HTML, or calculating text lengths.
* Exclude missing values when identifying descriptions shorter than 20 characters.
* Use clear section headings to make the printed report easy to read.
* Keep the implementation straightforward and readable rather than introducing unnecessary abstractions.

## Expected Output

Provide the complete Python implementation of `data_quality_report(df, text_columns)`.

When executed, the function should print a structured report containing:

* Basic dataset information
* Missing-value counts
* Duplicate counts
* Empty-value counts for text columns
* HTML detection counts
* Description-length statistics
* Counts and examples of descriptions shorter than 20 characters

The function does not need to return a new DataFrame.

## Validation

Verify that:

* The original DataFrame remains unchanged after running the function.
* Missing values are counted correctly.
* Duplicate rows and duplicate `app_id` values are reported separately.
* Whitespace-only strings are recognized as empty.
* HTML detection is performed for every specified text column.
* Length statistics are produced for every specified text column.
* Only non-missing descriptions shorter than 20 characters appear in the very-short-description check.
* No data-cleaning or filtering operations are performed.
"""
# Request: 2026-08-19 21:37 CET.
# Author: Sarah Chen (prompt and adjustments), ChatGPT (code)

# ===== 1. IMPORTS =====

import pandas as pd
from bs4 import BeautifulSoup

# ==== 2. CONFIGURATION =====

SRC = "data/raw/descriptions.zip"
OUT = "data/processed/descriptions_cleaned.zip"
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

df = pd.read_csv(SRC, escapechar="\\")

print(f"Loaded {len(df):,} rows.")

# # ===== 5. DATA QUALITY REPORT =====

data_quality_report(df, TEXT_COLUMNS)

# # ===== 6. PROCESS DATA =====

df_processed = df.copy()

for col in TEXT_COLUMNS:
    print(f"Removing HTML from {col}...")
    df_processed[col] = df_processed[col].apply(remove_html)

for col in TEXT_COLUMNS:
    df_processed = df_processed[df_processed[col].fillna("").str.strip().str.len() >= 20].copy()

# ===== 7. SAVE DATA INTO CSV =====

df_processed.to_csv(
    OUT,
    index=False,
    compression={
        "method": "zip",
        "archive_name": "descriptions_cleaned.csv"
    }
)
