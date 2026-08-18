### I will make the code more beautiful tomorrow,
### in case anyone actually already looked into this file :)


import pandas as pd
import json
import re
import numpy as np


df_raw = pd.read_csv(
    'data/games.csv',
    escapechar='\\'
)

def parse_price(x):
    if pd.isna(x) or x == '':
        return {}
    
    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}

price_data = df_raw['price_overview'].apply(parse_price)

# Turn the dictionaries into separate columns
price_df = pd.json_normalize(price_data)

# Add the prefix "price_"
price_df = price_df.add_prefix('price_')

# Combine with the original dataframe
df = pd.concat(
    [df_raw.drop(columns='price_overview'), price_df],
    axis=1
)

df['release_date'] = df['release_date'].replace('N', pd.NA)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df["is_free"] = df["is_free"].astype(bool)

# Create flag
df["full_audio_support"] = df["languages"].str.contains(
    "languages with full audio support",
    case=False,
    na=False
)

# Clean language column
df["languages"] = (
    df["languages"]
    .str.replace(r"<br\s*/?>.*$", "", regex=True)
    .str.replace(r"<[^>]+>", "", regex=True)
    .str.replace("*", "", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)
df["languages"] = df["languages"].replace("N", np.nan)


names_to_drop = [
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM!',
    'YEAH! YOU WANT "THOSE GAMES," RIGHT? SO HERE YOU GO! NOW, LET\'S SEE YOU CLEAR THEM! 2'
]

df = df[~df["name"].isin(names_to_drop)]

df["has_recurring_subscription"] = df["price_recurring_sub"].notna()
df["has_discount"] = df["price_discount_percent"].notna() & (df["price_discount_percent"] != 0)
df["language_count"] = (
    df["languages"]
    .str.split(",")
    .apply(lambda x: len(x) if isinstance(x, list) else 0)
)

#print(df.sort_values('release_date', ascending=False)['release_date'])
#print(df[df['release_date'] == '\N'])
#print(df[~df['is_free'].isin([0, 1])])
#print(df["languages"].value_counts())
#print(df['full_audio_support'].sum())
#print(df['price_recurring_sub_desc'])
#print(df.info())

df.to_excel("games.xlsx", index=False)