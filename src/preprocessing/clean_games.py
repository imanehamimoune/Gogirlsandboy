import pandas as pd
import json
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

price_df = pd.json_normalize(price_data)
price_df = price_df.add_prefix('price_')

df = pd.concat(
    [df_raw.drop(columns='price_overview'), price_df],
    axis=1
)

df['release_date'] = df['release_date'].replace('N', pd.NA)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df["is_free"] = df["is_free"].astype(bool)

df["full_audio_support"] = df["languages"].str.contains(
    "languages with full audio support",
    case=False,
    na=False
)

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

df["has_recurring_subscription"] = df["price_recurring_sub"].notna()
df["has_discount"] = (
    df["price_discount_percent"].notna()
    & (df["price_discount_percent"] != 0)
)

df["language_count"] = (
    df["languages"]
    .str.split(",")
    .apply(lambda x: len(x) if isinstance(x, list) else 0)
)

df.to_csv('games.csv', index=False)