
''' PART 2: EVALUATING PUBLISHER SCORES '''

'''
PROMPT

Role: You are a senior Data Engineer and Analyst with strong Python/Pandas expertise, building a weighted scoring and ranking layer on top of an existing publisher-level feature table. Prioritize transparency and easy adjustability of every weight/assumption over cleverness.
Context: Input is publisher_features.csv — one row per publisher_primary, already aggregated and normalized (contains raw features like review_score, avg_owners_mid, avg_language_count, avg_positive_review_ratio, avg_active_users_rate, recent_release_ratio, game_count, recent_release_count, plus their _norm counterparts where applicable). The next step is to combine these into 4 weighted dimension scores and one overall weighted score, then rank publishers by it.

Objective: Produce publisher_scores.csv — one row per publisher — containing the 4 dimension scores, the overall weighted score, and a rank. Do not touch publisher_features.csv itself.
Weighting scheme (as specified): Scale & Reach (35%) = 80% player count (reach) + 20% language count Quality (30%) = 50/50 split of review score and positive review ratio Engagement (20%) = no sub-weights specified Growth & Momentum (15%) = 60% ratio + 40% games count
Scope decisions to make explicit up front (state each as a code comment, collected in one clearly-labeled, easily-editable place — not buried in calculation logic):
* "Player count" and "language count" map to avg_owners_mid_norm and avg_language_count_norm respectively (the already-normalized reach features from publisher_features.csv).
* Quality has  a 50/50 blend sub-split of review_score (0-9) and avg_positive_review_ratio (0-1, already bounded). Before, min-max scale the review_score to 0-1 (only for this blend — do not alter or re-save review_score itself elsewhere). Make the blend weights a named, editable variable.
* Engagement has only one available signal (avg_active_users_rate_norm) -- no sub-split needed.
* "Ratio" in Growth & Momentum maps to recent_release_ratio (already bounded 0-1, matches the name directly).
* "Games count" in Growth & Momentum is recent_release_count_norm (recent releases only). 

Tasks:
1. Load publisher_features.csv and report its shape.
2. Collect every weight (the 4 dimension weights, and the sub-weights within Scale & Reach, Quality, and Growth & Momentum) into named dictionaries/variables at the top of the script, each asserted to sum to 1.0. No weight value should appear inline inside a calculation.
3. Min-max scale review_score (0-9) to 0-1 in a new column, since it must be combined with avg_positive_review_ratio (already 0-1) into the Quality dimension — document that publisher_features.csv intentionally left review_score unnormalized, and this rescale exists only for this combination step.
4. Compute the 4 dimension scores using the weighted sums defined above.
5. Compute overall_score as the weighted sum of the 4 dimension scores using the top-level weights. If any dimension score is NaN for a publisher, overall_score must also be NaN for that publisher (no silent reweighting or fabrication) — report these publishers separately rather than dropping them.
6. Rank publishers by overall_score (descending; ties get the same rank, e.g. via "min" ranking method). Sort the output by rank.
7. Execute and validate:
    * Actually run the code.
    * Confirm: all 4 dimension scores and overall_score fall within [0,1] (where non-NaN), no duplicate publishers, and report how many publishers have a NaN overall_score and why.
8. Deliver:
    * The code, plus a short summary: top 10-15 publishers by overall_score with their dimension breakdown.

Constraints (Do Not):
* Do not hardcode any weight inline in a formula — every weight must be a named variable/dict entry, changeable in one place.
* Do not silently reweight or impute a dimension score to cover a missing input — propagate NaN and report it instead.
* Do not drop any publisher row, including those that end up with a NaN overall_score.
* Do not alter or re-save publisher_features.csv.
* Do not pick a resolution for either ambiguous mapping (Quality sub-split, "games count") without stating it explicitly as an assumption in both a code comment and the delivered summary.
* Do not overengineer — no additional dimensions, no speculative features, no scaling beyond what's needed to combine review_score with avg_positive_review_ratio.

Expected Output:
* publisher_scores.csv: one row per publisher, containing rank, publisher_primary, game_count, the 4 dimension scores (scale_reach_score, quality_score, engagement_score, momentum_score), and overall_score.
* A short written summary covering: the top-ranked publishers with their dimension breakdown, and the two stated assumptions for review/override.

Validation:
* Reload the output and confirm: no duplicate publishers, all dimension scores and overall_score fall within [0,1] where present, and the count of publishers with a NaN overall_score matches the count reported in the summary.

'''
# Request: 2026-08-20 20:15 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)


"""
Score and rank publishers from publisher_features.csv using 4 weighted
dimensions. Structured to follow the task numbering in the source prompt
(Tasks 1-8) so each section below maps directly back to it.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.width", 140)

SRC_PUBLISHER_FEATURES = "data/analysis/publisher_features.csv"
OUT_PUBLISHER_SCORES = "data/analysis/publisher_scores.csv"

# =============================================================================
# TASK 1: LOAD
# =============================================================================
df = pd.read_csv(SRC_PUBLISHER_FEATURES, low_memory=False)
print("=" * 70)
print("TASK 1: LOAD")
print("=" * 70)
print("Loaded publisher_features.csv:", df.shape)

# =============================================================================
# TASK 2: WEIGHTS -- every weight named, editable in one place, sums to 1
# =============================================================================
# Scope decisions (stated explicitly, per the prompt):
#   - "Player count" / "language count" -> avg_owners_mid_norm /
#     avg_language_count_norm (already-normalized reach features).
#   - Quality as a 50/50 blend of
#     review_score (min-max'd to 0-1 in TASK 3) and avg_positive_review_ratio
#     (already 0-1).
#   - Engagement has only one signal (avg_active_users_rate_norm) -- no
#     sub-split needed.
#   - "Ratio" in Growth & Momentum -> recent_release_ratio (already 0-1,
#     matches the name directly).
#   - "Games count" in Growth & Momentum -> recent_release_count_norm
#     (recent releases only, NOT total portfolio size / game_count_norm).
print("\n" + "=" * 70)
print("TASK 2: WEIGHTS")
print("=" * 70)

DIMENSION_WEIGHTS = {
    "scale_reach_score": 0.35,
    "quality_score": 0.30,
    "engagement_score": 0.20,
    "momentum_score": 0.15,
}
assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-9, "dimension weights must sum to 1"

SCALE_REACH_WEIGHTS = {"avg_owners_mid_norm": 0.80, "avg_language_count_norm": 0.20}
assert abs(sum(SCALE_REACH_WEIGHTS.values()) - 1.0) < 1e-9, "scale & reach sub-weights must sum to 1"

QUALITY_WEIGHTS = {"review_score_norm": 0.50, "avg_positive_review_ratio": 0.50}
assert abs(sum(QUALITY_WEIGHTS.values()) - 1.0) < 1e-9, "quality sub-weights must sum to 1"

MOMENTUM_WEIGHTS = {"recent_release_ratio": 0.60, "recent_release_count_norm": 0.40}
assert abs(sum(MOMENTUM_WEIGHTS.values()) - 1.0) < 1e-9, "momentum sub-weights must sum to 1"

print("DIMENSION_WEIGHTS:", DIMENSION_WEIGHTS)
print("SCALE_REACH_WEIGHTS:", SCALE_REACH_WEIGHTS)
print("QUALITY_WEIGHTS:", QUALITY_WEIGHTS)
print("MOMENTUM_WEIGHTS:", MOMENTUM_WEIGHTS)

# =============================================================================
# TASK 3: RESCALE review_score FOR THE QUALITY BLEND ONLY
# =============================================================================
# publisher_features.csv intentionally left review_score (0-9) unnormalized
# to stay human-interpretable there. It's rescaled here, in a NEW column,
# only because this script needs to combine it with avg_positive_review_ratio
# (already 0-1) into a single Quality dimension. review_score itself is
# untouched and not re-saved.
print("\n" + "=" * 70)
print("TASK 3: RESCALE review_score (0-9 -> 0-1) FOR QUALITY BLEND")
print("=" * 70)
rs_min, rs_max = df["review_score"].min(), df["review_score"].max()
df["review_score_norm"] = (df["review_score"] - rs_min) / (rs_max - rs_min)
print(f"review_score range: [{rs_min}, {rs_max}] -> review_score_norm range: [0, 1]")

# =============================================================================
# TASK 4: DIMENSION SCORES
# =============================================================================
print("\n" + "=" * 70)
print("TASK 4: DIMENSION SCORES")
print("=" * 70)
df["scale_reach_score"] = sum(df[c] * w for c, w in SCALE_REACH_WEIGHTS.items())
df["quality_score"] = sum(df[c] * w for c, w in QUALITY_WEIGHTS.items())
df["engagement_score"] = df["avg_active_users_rate_norm"]
df["momentum_score"] = sum(df[c] * w for c, w in MOMENTUM_WEIGHTS.items())
print("Computed: scale_reach_score, quality_score, engagement_score, momentum_score")

# =============================================================================
# TASK 5: OVERALL SCORE -- NaN in any dimension propagates, never reweighted
# =============================================================================
print("\n" + "=" * 70)
print("TASK 5: OVERALL SCORE")
print("=" * 70)
DIMS = ["scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
df["overall_score"] = sum(df[c] * DIMENSION_WEIGHTS[c] for c in DIMS)

nan_overall = df["overall_score"].isna()
print(f"Publishers with NaN overall_score: {nan_overall.sum()}")
if nan_overall.sum() > 0:
    nan_reasons = df.loc[nan_overall, DIMS].isna()
    print("Which dimension(s) caused it (count of publishers missing each):")
    print(nan_reasons.sum().to_string())

# =============================================================================
# TASK 6: RANK
# =============================================================================
print("\n" + "=" * 70)
print("TASK 6: RANK")
print("=" * 70)
df["rank"] = df["overall_score"].rank(ascending=False, method="min").astype("Int64")
df = df.sort_values("overall_score", ascending=False, na_position="last")
print("Ranked by overall_score, descending, ties share the same rank (method='min').")

# =============================================================================
# TASK 7: EXECUTE AND VALIDATE
# =============================================================================
print("\n" + "=" * 70)
print("TASK 7: EXECUTE AND VALIDATE")
print("=" * 70)
for c in DIMS + ["overall_score"]:
    vals = df[c].dropna()
    in_range = vals.between(0, 1).all()
    print(f"  {c:20s} min={vals.min():.3f}  max={vals.max():.3f}  within [0,1]: {in_range}  NaN count={df[c].isna().sum()}")

dup_count = df["publisher_primary"].duplicated().sum()
print(f"\nduplicate publishers: {dup_count}")
print(f"NaN overall_score count matches TASK 5 report: {df['overall_score'].isna().sum() == nan_overall.sum()}")

# =============================================================================
# SAVE
# =============================================================================
final_cols = ["rank", "publisher_primary", "game_count"] + DIMS + ["overall_score"]
df[final_cols].to_csv(OUT_PUBLISHER_SCORES, index=False)
print(f"\nSaved: {OUT_PUBLISHER_SCORES}  shape={df[final_cols].shape}")

# =============================================================================
# TASK 8: DELIVER (short summary)
# =============================================================================
print("\n" + "=" * 70)
print("TASK 8: SUMMARY")
print("=" * 70)
print("Top 15 publishers by overall_score:")
print(df[final_cols].head(15).to_string(index=False))

print("\nAssumptions applied (stated for review/override):")
print("  1. Quality (30%) = 50/50 blend of review_score_norm and avg_positive_review_ratio")
print("     (no sub-split was specified; review_score min-max'd to 0-1 only for this blend).")
print("  2. Growth & Momentum 'games count' (40% of the 15% dimension) = "
      "recent_release_count_norm (recent releases only, not total portfolio size).")

'''
PROMPT:

Using df (already in memory from earlier in the script — after overall_score and the 4 dimension scores have been computed on it), generate 3 plots:

Top 10 by overall_score — horizontal bar chart, solid green, ranked descending (highest at top), value labeled at the end of each bar.
Top 3 acquisition candidates vs. Xbox — dimension breakdown — grouped vertical bar chart. Take the top 3 publishers by overall_score (excluding PlayStation Publishing LLC), plus Xbox Game Studios fixed in as a reference point regardless of its own rank. Show all 4 dimension scores side-by-side per publisher, each dimension a different color, values labeled above each bar.
Top 10 per individual dimension — 2×2 grid, one panel per dimension, each independently showing its own top 10 publishers (not the overall top 10) as solid-green horizontal bars, value-labeled.

Save the output in data/analysis/publisher_score_plots/ as plot1_top10_overall.png, plot2_top3_acquisition_candidates.png, and plot3_top10_per_dimension.png respectively. Use a consistent color scheme for the 4 dimensions across all plots, and ensure all text is legible (font size, rotation, etc.).
'''
# Request: 2026-08-20 22:53 CET.
# Author: Anna Andruszkiewicz (prompt and adjustments), Claude (code)

DIMS = ["scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
LABELS = {"scale_reach_score": "Scale & Reach", "quality_score": "Quality",
          "engagement_score": "Engagement", "momentum_score": "Growth & Momentum"}
COLORS = {"scale_reach_score": "#4C72B0", "quality_score": "#55A868",
          "engagement_score": "#C44E52", "momentum_score": "#DD8452"}

top10 = df.head(10)



# --- Plot 1: Top 10 by overall_score (solid green) -------------------------
fig, ax = plt.subplots(figsize=(9, 6))
plot_order = top10.iloc[::-1]
bars = ax.barh(plot_order["publisher_primary"], plot_order["overall_score"], color="green")
for bar, val in zip(bars, plot_order["overall_score"]):
    ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Overall Score")
ax.set_title("Top 10 Publishers by Overall Score", fontsize=13, fontweight="bold")
ax.set_xlim(0, top10["overall_score"].max() * 1.15)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("data/analysis/publisher_score_plots/plot1_top10_overall.png", dpi=150)
plt.close()

# --- Plot 2: Acquisition candidates -- dimension scores (grouped, colored) -
EXCLUDE_PUBLISHERS = ["PlayStation Publishing LLC"]
XBOX_PUBLISHER = "Xbox Game Studios"  # adjust to match the exact string in your data

pool = df[~df["publisher_primary"].isin(EXCLUDE_PUBLISHERS)]

top3 = pool.nlargest(3, "overall_score")
xbox_row = pool[pool["publisher_primary"] == XBOX_PUBLISHER]

candidates = pd.concat([top3, xbox_row]).drop_duplicates(subset="publisher_primary")

x = np.arange(len(candidates))
width = 0.2
fig, ax = plt.subplots(figsize=(15, 7))
for i, d in enumerate(DIMS):
    offset = (i - 1.5) * width
    bars = ax.bar(x + offset, candidates[d], width, label=LABELS[d], color=COLORS[d])
    for bar, val in zip(bars, candidates[d]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
ax.set_xticks(x)
ax.set_xticklabels(candidates["publisher_primary"], rotation=25, ha="right")
ax.set_ylabel("Dimension Score (0-1, scaled against all publishers)")
ax.set_title("Top 3 Acquisition Candidates -- Dimension Scores", fontsize=13, fontweight="bold")
ax.set_ylim(0, 1.15)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("data/analysis/publisher_score_plots/plot2_top3_across_dimensions.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Plot 3: Top 10 per individual dimension (2x2 grid, solid green) -------
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
for ax, d in zip(axes.flat, DIMS):
    top10_dim = df.dropna(subset=[d]).nlargest(10, d).iloc[::-1]
    bars = ax.barh(top10_dim["publisher_primary"], top10_dim[d], color="green")
    for bar, val in zip(bars, top10_dim[d]):
        ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=8)
    ax.set_xlabel(f"{LABELS[d]} Score")
    ax.set_xlim(0, top10_dim[d].max() * 1.15)
    ax.set_title(f"Top 10 by {LABELS[d]}", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Top 10 Publishers per Individual Dimension", fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("data/analysis/publisher_score_plots/plot3_top10_per_dimension.png", dpi=150, bbox_inches="tight")
plt.close()