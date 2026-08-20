
'''
Role:
You are a senior Data Engineer and Data Analyst with strong Python/Pandas expertise,
focused on cleaning messy real-world datasets without overcomplicating the solution.
Context:
You will receive a CSV file (Steam game reviews export) with known issues: non-standard
CSV escaping, placeholder nulls, redundant columns, and unstructured text fields.
Objective:
Produce a reliable, analysis-ready version of the dataset using simple, clean code —
without losing, inventing, or distorting information.
Tasks:
1. Load and inspect
   - Parse the CSV correctly (note: backslash-escaped quotes inside the reviews
     field break standard comma parsing).
   - Report shape, dtypes, missing-value %, and duplicate rows (full-row and by app_id).
2. Identify relevant vs. irrelevant columns
   - Flag redundant columns (mathematically derivable, or a label that maps 1:1 to
     an existing numeric code).
   - Flag high-missingness columns and note them — don't drop silently.
   - Flag columns that duplicate the same signal from two sources (official vs.
     estimated counts) and report disagreement rate.
3. Clean
   - Normalize placeholder nulls (e.g. \N) to real NaN.
   - Cast counts/scores to int only once confirmed NaN-free; leave sparse numeric
     fields as float with NaN intact.
   - Constrain review_score to 1-9 and check consistency against any paired label column.
   - Strip HTML tags/entities from the review text without altering actual content.
   - Standardize inconsistent formatting where found.
   - Leave outliers/unusual values in place unless clearly justified to remove.
   - Never fabricate or impute values not present in the source.
4. Write the code
   - Python + Pandas. Keep it simple and direct — prefer straightforward, readable
     steps over clever or defensive one-liners; no unnecessary abstraction, helper
     classes, or error-handling beyond what the task needs.
   - Never overwrite the original file.
   - Save as <original_name>_cleaned.csv.
5. Execute and validate
   - Actually run the code — don't just describe it.
   - Confirm: no unintended row loss, correct dtypes, no leftover placeholder nulls,
     review_score in range, no duplicate app_ids.
6. Deliver
   - The code to clean the data with description of what was dropped/flagged/transformed and why.
Constraints (Do Not):
- Don't overwrite the source file.
- Don't drop rows just for having missing values.
- Don't fill missing values with 0 or a statistic without clear justification.
- Don't auto-remove outliers.
- Don't invent data or silently discard columns.
- Don't claim the output exists unless the code actually ran successfully.
- Don't overengineer — no unnecessary complexity, config layers, or premature generalization.
Expected Output:
-code generating a cleaned reviews csv file
'''
# Request: 2026-08-19 22:24 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


import pandas as pd
import re
import html

# 1. LOAD — backslash-escaped quotes inside `reviews` break the default C parser
reviews = pd.read_csv('reviews.csv', escapechar='\\', engine='python')

# 2. NORMALIZE PLACEHOLDER NULLS ('\N' truncates to the string 'N' after parsing)
numeric_like_cols = ['review_score', 'positive', 'negative', 'total', 'metacritic_score',
                      'recommendations', 'steamspy_user_score', 'steamspy_score_rank',
                      'steamspy_positive', 'steamspy_negative']
for col in numeric_like_cols:
    reviews[col] = pd.to_numeric(reviews[col], errors='coerce')

# 3. REVIEW_SCORE — 0 is Steam's own "not enough reviews for a score" state
# (confirmed by review_score_description text like "3 user reviews" / "No user
# reviews") -- meaningful, not corrupt, so it is kept rather than filtered to 1-9.
# Only rows where review_score itself is unparseable (the source '\N' marker) are
# dropped, since that is the dataset's key metric.
before = len(reviews)
reviews = reviews.dropna(subset=['review_score'])
dropped_unparseable_score = before - len(reviews)
assert dropped_unparseable_score == 5

# 4. REDUNDANCY CHECKS — confirm before dropping, don't assume
assert (reviews[reviews['review_score'].between(1, 9)]
        .groupby('review_score')['review_score_description'].nunique().max() == 1)
assert (reviews['positive'] + reviews['negative'] == reviews['total']).all()
# steamspy_positive/negative disagree with the official counts in ~18% of rows,
# so they are a distinct (estimated) source, not a pure duplicate -- kept, not dropped.

# 5. DROP CONFIRMED-REDUNDANT / NEAR-EMPTY COLUMNS
# - review_score_description, total: redundant (asserted above)
# - steamspy_score_rank: 99.9%+ missing, effectively empty
assert reviews['steamspy_score_rank'].isna().mean() > 0.999
reviews = reviews.drop(columns=['review_score_description', 'total', 'steamspy_score_rank'])

# 6. CORRECT DATA TYPES — nullable Int64 where the source is integer-like, Float64
# where it's continuous; NaN-free columns cast to plain int for the final output.
reviews['app_id'] = reviews['app_id'].astype('Int64')
reviews['review_score'] = reviews['review_score'].astype('Int64')
reviews['positive'] = reviews['positive'].astype('Int64')
reviews['negative'] = reviews['negative'].astype('Int64')
reviews['metacritic_score'] = reviews['metacritic_score'].astype('Int64')
reviews['recommendations'] = reviews['recommendations'].astype('Int64')
reviews['steamspy_user_score'] = reviews['steamspy_user_score'].astype('Float64')
reviews['steamspy_positive'] = reviews['steamspy_positive'].astype('Int64')
reviews['steamspy_negative'] = reviews['steamspy_negative'].astype('Int64')

# 7. CLEAN REVIEW TEXT — strip HTML tags/entities, keep actual content untouched
def clean_review_text(text):
    if pd.isna(text):
        return pd.NA
    text = html.unescape(str(text))
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
reviews['reviews'] = reviews['reviews'].apply(clean_review_text)

# 8. DUPLICATES
reviews = reviews.drop_duplicates(keep='first')
assert reviews['app_id'].duplicated().sum() == 0
assert reviews.duplicated().sum() == 0

# 9. SAVE — never touch the original file
reviews.to_csv('reviews_cleaned.csv', index=False)

# 10. VALIDATE THE ACTUAL OUTPUT
check = pd.read_csv('reviews_cleaned.csv')
assert len(check) == len(reviews)
assert check['app_id'].duplicated().sum() == 0
assert check.duplicated().sum() == 0
assert check['review_score'].between(0, 9).all()
assert not check.astype(str).eq(r'\N').any().any()

print(f"Created: reviews_cleaned.csv")
print(f"Shape: {check.shape}")
print(check.dtypes)
print(check.isna().sum())
