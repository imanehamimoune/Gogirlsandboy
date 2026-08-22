'''# Master Prompt: Games CSV Cleaning and Transformation

## Role

You are an expert Data Analyst and Python/Pandas Data Engineer specializing in data cleaning, preprocessing, transformation, and reproducible data pipelines.

Your task is to generate a **complete Python script** that loads a raw games CSV file, performs all specified cleaning and feature-engineering steps, and saves the resulting cleaned dataset as a new CSV file.

The generated code must be **fully executable as provided**.

---

## Input and Output

Use exactly these paths:

```python
INPUT_PATH = "data/raw/games.zip"
OUTPUT_PATH = "data/processed/games_cleaned.csv"

```

Do **not** use any other input or output path.

The script should read the input CSV using:

```python
pd.read_csv(
    INPUT_PATH,
    escapechar='\\'
)

```

The final cleaned DataFrame must be written using:

```python
df.to_csv(OUTPUT_PATH, index=False)

```

---

# Required Processing Steps

The generated Python code must perform **all** of the following steps, in the specified order.

Do not omit, simplify, replace, or reinterpret any of these transformations.

---

## 1. Import Required Libraries

The script must import:

```python
import pandas as pd
import json
import numpy as np

```

You may additionally import `os` or `pathlib.Path` if needed to create the output directory, but the core processing logic must remain unchanged.

---

## 2. Load the Raw CSV

Load the dataset from:

```text
data/raw/games.csv

```

using Pandas and `escapechar='\\'`.

Store the raw DataFrame in:

```python
df_raw

```

Equivalent required logic:

```python
df_raw = pd.read_csv(
    INPUT_PATH,
    escapechar='\\'
)

```

---

## 3. Parse the `price_overview` Column

The `price_overview` column contains JSON-like strings that need to be parsed.

Create a function called:

```python
parse_price(x)

```

with the following behavior:

- If the value is missing (`NaN`) or an empty string, return an empty dictionary `{}`.
- Otherwise, attempt to parse the value using `json.loads()`.
- If parsing fails because of `json.JSONDecodeError` or `TypeError`, return `{}`.

The logic must be equivalent to:

```python
def parse_price(x):
    if pd.isna(x) or x == '':
        return {}

    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}

```

Apply this function to:

```python
df_raw['price_overview']

```

and store the result in:

```python
price_data

```

---

## 4. Normalize the Price JSON Data

Convert the parsed price dictionaries into separate columns using:

```python
pd.json_normalize(price_data)

```

Store the resulting DataFrame in:

```python
price_df

```

Then add the prefix:

```text
price_

```

to every generated price column.

Equivalent logic:

```python
price_df = pd.json_normalize(price_data)
price_df = price_df.add_prefix('price_')

```

---

## 5. Combine the Price Columns with the Original Dataset

Remove the original:

```text
price_overview

```

column from the raw dataset.

Then concatenate the remaining raw columns with the normalized price DataFrame horizontally.

The resulting DataFrame must be stored in:

```python
df

```

Equivalent logic:

```python
df = pd.concat(
    [df_raw.drop(columns='price_overview'), price_df],
    axis=1
)

```

---

# 6. Clean and Convert `release_date`

The `release_date` column may contain the string:

```text
N

```

Replace these values with `pd.NA`.

Then convert the column to Pandas datetime using:

```python
pd.to_datetime(
    df['release_date'],
    errors='coerce'
)

```

The resulting column must therefore contain proper datetime values where possible and `NaT` where conversion fails.

Required logic:

```python
df['release_date'] = df['release_date'].replace('N', pd.NA)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

```

---

# 7. Convert `is_free` to Boolean

Convert the `is_free` column to Boolean using:

```python
df["is_free"] = df["is_free"].astype(bool)

```

Do not use a different Boolean-conversion approach.

---

# 8. Create `full_audio_support`

Create a new column:

```text
full_audio_support

```

based on the `languages` column.

The value should be `True` when the `languages` string contains:

```text
languages with full audio support

```

The search must:

- be case-insensitive
- handle missing values safely

Required logic:

```python
df["full_audio_support"] = df["languages"].str.contains(
    "languages with full audio support",
    case=False,
    na=False
)

```

---

# 9. Clean the `languages` Column

Clean the `languages` column using the following exact sequence of transformations.

### Step 1

Remove everything starting from a `<br>` HTML tag through the end of the string.

The regex must support both:

```text
<br>
<br/>
<br />

```

Use:

```python
.str.replace(r"<br\s*/?>.*$", "", regex=True)

```

### Step 2

Remove remaining HTML tags:

```python
.str.replace(r"<[^>]+>", "", regex=True)

```

### Step 3

Remove literal asterisks:

```python
.str.replace("*", "", regex=False)

```

### Step 4

Collapse consecutive whitespace into a single space:

```python
.str.replace(r"\s+", " ", regex=True)

```

### Step 5

Strip leading and trailing whitespace:

```python
.str.strip()

```

The complete transformation must be equivalent to:

```python
df["languages"] = (
    df["languages"]
    .str.replace(r"<br\s*/?>.*$", "", regex=True)
    .str.replace(r"<[^>]+>", "", regex=True)
    .str.replace("*", "", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

```

After cleaning, replace the literal string:

```text
N

```

with:

```python
np.nan

```

using:

```python
df["languages"] = df["languages"].replace("N", np.nan)

```

---

# 10. Remove Two Specific Invalid Game Entries

Remove rows where the `name` column is exactly equal to either of these two values:

```text
YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET'S SEE YOU CLEAR THEM!

```

or:

```text
YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET'S SEE YOU CLEAR THEM! 2

```

Create a list containing these two names:

```python
names_to_drop = [
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM!',
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM! 2'
]

```

Then remove those rows using:

```python
df = df[~df["name"].isin(names_to_drop)]

```

Do not remove any other game entries.

---

# 11. Keep Price Data Only for EUR

Create exactly this list of price-related columns:

```python
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

```

For every row where:

```text
price_currency != "EUR"

```

set all of these columns to:

```python
np.nan

```

Use the equivalent logic:

```python
df.loc[df['price_currency'] != 'EUR', cols] = np.nan

```

This means that **all price-related information in those columns must be discarded for non-EUR currencies**.

Do not convert currencies.

Do not perform exchange-rate calculations.

Do not attempt to infer missing currencies.

---

# 12. Create `has_recurring_subscription`

Create a new Boolean column:

```text
has_recurring_subscription

```

It must be `True` whenever `price_recurring_sub` is not missing and `False` otherwise.

Use:

```python
df["has_recurring_subscription"] = df["price_recurring_sub"].notna()

```

---

# 13. Create `has_discount`

Create a new Boolean column:

```text
has_discount

```

It must be `True` when:

1. `price_discount_percent` is not missing, AND
2. `price_discount_percent` is not equal to `0`.

Use exactly:

```python
df["has_discount"] = (
    df["price_discount_percent"].notna()
    & (df["price_discount_percent"] != 0)
)

```

Do not infer discounts from other price columns.

---

# 14. Create `language_count`

Create a new column:

```text
language_count

```

based on the cleaned `languages` column.

The calculation must:

- split the string using a comma `,`
- count the resulting list elements
- return `0` when the value is not a list, such as when the language value is missing

Use the equivalent logic:

```python
df["language_count"] = (
    df["languages"]
    .str.split(",")
    .apply(lambda x: len(x) if isinstance(x, list) else 0)
)

```

Do not use a different language-counting methodology.

---

# 15. Save the Final Dataset

Save the final DataFrame to exactly:

```text
data/processed/games_cleaned.csv

```

using:

```python
df.to_csv(OUTPUT_PATH, index=False)

```

The output must not contain the Pandas index as an additional column.

If necessary, create the parent output directory before saving. Do not change the specified output path.

---

# Important Requirements

## Reproducibility

The generated Python script must be self-contained and executable from the project root.

Do not assume that any variables from another script already exist.

Do not rely on previously processed data.

The script must always start from:

```text
data/raw/games.csv

```

and independently produce:

```text
data/processed/games_cleaned.csv

```

## Do Not Add Additional Transformations

Do **not**:

- remove additional columns
- remove additional rows
- rename existing columns
- change the price logic
- convert currencies
- add extra feature engineering
- perform additional missing-value imputation
- standardize numerical variables
- remove duplicates
- sort the DataFrame
- change the data types beyond the explicitly requested conversions
- modify the cleaning rules

The goal is to reproduce the specified processing pipeline exactly.

## Code Quality

The final response must contain the complete Python code and nothing that requires manual implementation.

Use clear section comments so that each processing stage is easy to identify.

The final script should be suitable for placing directly into a Python project, for example:

```text
src/
└── feature_engineering/
    └── clean_games.py

```

When executed from the project root, it should read:

```text
data/raw/games.csv

```

and create:

```text
data/processed/games_cleaned.csv

```

The generated code must implement **every transformation described above in the exact order specified**.'''

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
