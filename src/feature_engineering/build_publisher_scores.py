# ---------------------------------------------------------------------------
# Build features on publisher level from game-level data
# ---------------------------------------------------------------------------
"""
Build publisher_features.csv from master_dataset.csv: one row per
primary_publisher, aggregating game-level data into 8 features. Publishers
with fewer than MIN_GAMES titles are dropped (too few games for a
publisher-level average to be meaningful/stable).

Features (all aggregated per publisher):
  - review_score            : mean of review_score (0-9), EXCLUDING 0 --
                               0 signals "too few reviews to score", not an
                               actually bad score, so including it would
                               wrongly drag the average down for a publisher
                               that's simply under-reviewed, not disliked.
  - avg_owners_mid           : mean of owners_mid (reach per game)
  - avg_language_count       : mean of language_count (localization reach)
  - avg_positive_review_ratio: mean of positive/(positive+negative) per game
                               (already 0-1, games with zero reviews at all
                               are NaN and excluded from the mean, not
                               treated as 0% positive)
  - avg_active_users_rate    : mean of concurrent_users_yesterday/owners_mid
                               per game (already conceptually 0-1, but see
                               normalization note below -- it isn't reliably
                               bounded in this data)
  - recent_release_count     : count of games released within RECENT_YEARS
                               of the dataset's own max release_date
  - recent_release_ratio     : recent_release_count / game_count (0-1)
  - game_count               : portfolio size (games per publisher)
    - avg_price                : mean of price_final_clean (EUR) per game,
                                LEFT UNNORMALIZED on purpose -- not a
                                dimension score, but a raw input for a
                                downstream revenue estimate (e.g.
                                avg_owners_mid * avg_price), which needs
                                real EUR units, not a scaled 0-1 value.
                                Free games correctly contribute 0; games
                                with unverified/non-EUR pricing are NaN
                                and excluded from the mean, not guessed at.

Normalization (proposed and applied):
  - avg_owners_mid, avg_language_count, game_count, recent_release_count
      -> log1p + min-max. These are count/count-derived aggregates and are
         heavily right-skewed (a few large publishers, many small ones);
         log1p compresses the tail before scaling to [0,1]. Method choice
         is confirmed by computed skew on THIS aggregated data (>2 -> log),
         not assumed.
  - avg_active_users_rate
      -> percentile rank, not log+min-max. This ratio is not reliably
         bounded in the source data -- a handful of games have
         steamspy-bucket-mismatched owners_mid producing rates that even
         log1p doesn't tame, which would crush every other publisher
         toward 0 after min-max. Percentile rank is immune to how extreme
         an outlier is.
  - review_score (0-9), avg_positive_review_ratio, recent_release_ratio
      -> left as-is. Already bounded and directly interpretable; scaling
         them further would only obscure the original scale for no
         analytical benefit.
"""
import zipfile
import numpy as np
import pandas as pd

pd.set_option("display.width", 140)

SRC = "data/processed/master_dataset.zip"
OUT = "data/processed/publisher_features.csv"
MIN_GAMES = 10
RECENT_YEARS = 2

with zipfile.ZipFile(SRC) as z:
    with z.open("master_dataset.csv") as f:
        df = pd.read_csv(f, low_memory=False)

print("Loaded master_dataset.csv:", df.shape)

# ---------------------------------------------------------------------------
# PER-GAME PREP (before aggregating)
# ---------------------------------------------------------------------------
review_denom = df["positive"] + df["negative"]
df["review_positive_ratio"] = np.where(review_denom > 0, df["positive"] / review_denom, np.nan)
df["active_users_rate"] = np.where(df["owners_mid"] > 0, df["concurrent_users_yesterday"] / df["owners_mid"], np.nan)

df["release_date_parsed"] = pd.to_datetime(df["release_date"], errors="coerce")
reference_today = df["release_date_parsed"].max()
df["is_recent"] = (reference_today - df["release_date_parsed"]).dt.days / 365.25 <= RECENT_YEARS
print(f"Reference 'today' (max release_date in data): {reference_today.date()}")

# review_score: 0 means "too few reviews to compute a score", not "bad" --
# treat as missing for averaging purposes, not as a real 0.
df["review_score_for_avg"] = df["review_score"].replace(0, np.nan)

# rows with no primary_publisher can't be aggregated -- report, don't guess
missing_pub = df["primary_publisher"].isna().sum()
print(f"Rows with missing primary_publisher (excluded from aggregation): {missing_pub} ({missing_pub/len(df)*100:.1f}%)")

df["est_revenue_per_game"] = df["owners_mid"] * df["price_final_clean"]

# ---------------------------------------------------------------------------
# AGGREGATE TO PUBLISHER LEVEL
# ---------------------------------------------------------------------------
grouped = df.groupby("primary_publisher")
publisher_features = grouped.agg(
    game_count=("app_id", "count"),
    review_score=("review_score_for_avg", "mean"),
    avg_owners_mid=("owners_mid", "mean"),
    avg_language_count=("language_count", "mean"),
    avg_positive_review_ratio=("review_positive_ratio", "mean"),
    avg_active_users_rate=("active_users_rate", "mean"),
    recent_release_count=("is_recent", "sum"),
    avg_price=("price_final_clean", "mean"),
    total_est_revenue=("est_revenue_per_game", "sum"),    
    avg_est_revenue_per_game=("est_revenue_per_game", "mean"),
    max_single_game_revenue=("est_revenue_per_game", "max"),  
).reset_index()



publisher_features["recent_release_ratio"] = (
    publisher_features["recent_release_count"] / publisher_features["game_count"]
)

print(f"\nPublishers before game_count filter: {len(publisher_features)}")
publisher_features = publisher_features[publisher_features["game_count"] >= MIN_GAMES].copy()
print(f"Publishers with game_count >= {MIN_GAMES}: {len(publisher_features)}")

# ---------------------------------------------------------------------------
# NORMALIZATION (method chosen per feature, justified above; skew computed
# live on this aggregated/filtered data, not assumed)
# ---------------------------------------------------------------------------
SKEW_THRESHOLD = 2.0
log_minmax_candidates = ["avg_owners_mid", "avg_language_count", "game_count", "recent_release_count"]
rank_scaled = ["avg_active_users_rate"]

print("\nNormalization applied:")
for col in log_minmax_candidates:
    col_skew = publisher_features[col].skew()
    if abs(col_skew) > SKEW_THRESHOLD:
        transformed = np.log1p(publisher_features[col])
        method = "log1p + min-max"
    else:
        transformed = publisher_features[col]
        method = "min-max"
    col_min, col_max = transformed.min(), transformed.max()
    publisher_features[col + "_norm"] = (transformed - col_min) / (col_max - col_min)
    print(f"  {col:24s} skew={col_skew:7.2f}  method={method}")

for col in rank_scaled:
    publisher_features[col + "_norm"] = publisher_features[col].rank(pct=True)
    print(f"  {col:24s}              method=percentile rank")

print("\nLeft unnormalized (already bounded/interpretable): review_score (0-9), "
      "avg_positive_review_ratio (0-1), recent_release_ratio (0-1)")

# ---------------------------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)
print("shape:", publisher_features.shape)
print("duplicate publishers:", publisher_features["primary_publisher"].duplicated().sum())
inf_check = np.isinf(publisher_features.select_dtypes(include=[np.number])).sum()
print("columns with inf/-inf:", inf_check[inf_check > 0].to_dict() or "none")
print("\nmissing % per column:")
print((publisher_features.isna().mean() * 100).round(2).to_string())

print("\nTop 10 by review_score (min 10 games, 0s excluded from average):")
print(publisher_features.nlargest(10, "review_score")[["primary_publisher", "game_count", "review_score"]].to_string(index=False))

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
publisher_features.to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={publisher_features.shape}")


# ---------------------------------------------------------------------------
# Score and rank publishers from publisher_features.csv using 4 weighted dimensions
# ---------------------------------------------------------------------------
"""
Score and rank publishers from publisher_features.csv using 4 weighted
dimensions. All weights are collected in WEIGHTS below -- edit there, not
in the calculation logic, to change any assumption.

Dimension formulas (as specified):
  Scale & Reach (35%)     = 80% avg_owners_mid_norm + 20% avg_language_count_norm
  Quality (30%)           = NOT sub-weighted by the user -- publisher_features.csv
                             has two quality signals (review_score 0-9,
                             avg_positive_review_ratio 0-1). DEFAULT: 50/50
                             blend of both (review_score min-max'd to 0-1
                             first). Change QUALITY_WEIGHTS below to use
                             just one if that's what was meant.
  Engagement (20%)        = avg_active_users_rate_norm (only engagement
                             signal available, no sub-split needed)
  Growth & Momentum (15%) = 60% recent_release_ratio + 40% "games count".
                             AMBIGUOUS which count was meant:
                               - game_count_norm (total portfolio size) <- DEFAULT
                               - recent_release_count_norm (recent releases only)
                             game_count_norm is used by default since it's the
                             more literal name match, but recent_release_count
                             arguably fits a "momentum" dimension better
                             conceptually. Swap MOMENTUM_COUNT_COL below to
                             switch.

overall_score = weighted sum of the 4 dimension scores. NaN in a dimension
propagates to NaN in overall_score for that publisher (not silently
reweighted) -- these are reported separately, not dropped or guessed.

Also generates 5 plots in the same run:
  1. Top 10 publishers by overall_score (bar chart)
  2. Top 5 publishers -- % contribution of each dimension (STACKED bar chart)
  3. Top 10 publishers by review_score (0-9), bar chart
  4. Top 10 publishers per individual dimension -- Scale & Reach, Quality,
     Engagement, Growth & Momentum each get their own horizontal bar chart
     (2x2 grid), each independently sorted/ranked by that one dimension
     (not necessarily the same 10 publishers as the overall top 10)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SRC = "data/feature_analysis/publisher_features.csv"
OUT = "data/feature_analysis/publisher_scores.csv"
PLOT_DIR = "reports/plots/"

# ---------------------------------------------------------------------------
# WEIGHTS -- edit here to change any assumption
# ---------------------------------------------------------------------------
DIMENSION_WEIGHTS = {
    "scale_reach_score": 0.35,
    "quality_score": 0.30,
    "engagement_score": 0.20,
    "momentum_score": 0.15,
}
assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-9, "dimension weights must sum to 1"

SCALE_REACH_WEIGHTS = {"avg_owners_mid_norm": 0.80, "avg_language_count_norm": 0.20}
assert abs(sum(SCALE_REACH_WEIGHTS.values()) - 1.0) < 1e-9

QUALITY_WEIGHTS = {"review_score_norm": 0.50, "avg_positive_review_ratio": 0.50}
assert abs(sum(QUALITY_WEIGHTS.values()) - 1.0) < 1e-9

MOMENTUM_COUNT_COL = "game_count_norm"  # alternative: "recent_release_count_norm"
MOMENTUM_WEIGHTS = {"recent_release_ratio": 0.60, MOMENTUM_COUNT_COL: 0.40}
assert abs(sum(MOMENTUM_WEIGHTS.values()) - 1.0) < 1e-9

df = pd.read_csv(SRC, low_memory=False)
print("Loaded publisher_features.csv:", df.shape)

# ---------------------------------------------------------------------------
# review_score (0-9) needs its own min-max to 0-1 to be combined with
# avg_positive_review_ratio (already 0-1) into the Quality dimension --
# publisher_features.csv left review_score unnormalized on purpose (per
# earlier decision to keep it human-interpretable there); it's normalized
# here only because this script needs to combine it with another 0-1 metric.
# ---------------------------------------------------------------------------
rs_min, rs_max = df["review_score"].min(), df["review_score"].max()
df["review_score_norm"] = (df["review_score"] - rs_min) / (rs_max - rs_min)

# ---------------------------------------------------------------------------
# DIMENSION SCORES
# ---------------------------------------------------------------------------
df["scale_reach_score"] = sum(df[c] * w for c, w in SCALE_REACH_WEIGHTS.items())
df["quality_score"] = sum(df[c] * w for c, w in QUALITY_WEIGHTS.items())
df["engagement_score"] = df["avg_active_users_rate_norm"]
df["momentum_score"] = sum(df[c] * w for c, w in MOMENTUM_WEIGHTS.items())

# ---------------------------------------------------------------------------
# OVERALL SCORE + RANK
# ---------------------------------------------------------------------------
df["overall_score"] = sum(df[c] * w for c, w in DIMENSION_WEIGHTS.items())
df["rank"] = df["overall_score"].rank(ascending=False, method="min").astype("Int64")
df = df.sort_values("overall_score", ascending=False)

# ---------------------------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------------------------
print("\nDimension score ranges (should all be ~0-1):")
for c in ["scale_reach_score", "quality_score", "engagement_score", "momentum_score", "overall_score"]:
    print(f"  {c:20s} min={df[c].min():.3f}  max={df[c].max():.3f}  NaN count={df[c].isna().sum()}")

print("\nduplicate publishers:", df["primary_publisher"].duplicated().sum())

print("\nTop 15 publishers by overall_score:")
print(df[["rank", "primary_publisher", "game_count", "scale_reach_score",
          "quality_score", "engagement_score", "momentum_score", "overall_score"]]
      .head(15).to_string(index=False))

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------
final_cols = [
    "rank", "primary_publisher", "game_count",
    "scale_reach_score", "quality_score", "engagement_score", "momentum_score",
    "overall_score",
]
#df[final_cols].to_csv(OUT, index=False)
#print(f"\nSaved: {OUT}  shape={df[final_cols].shape}")

# ---------------------------------------------------------------------------
# PLOTS
# ---------------------------------------------------------------------------
DIMS = ["scale_reach_score", "quality_score", "engagement_score", "momentum_score"]
LABELS = {
    "scale_reach_score": "Scale & Reach",
    "quality_score": "Quality",
    "engagement_score": "Engagement",
    "momentum_score": "Growth & Momentum",
}
COLORS = {
    "scale_reach_score": "#5B9BD5",   # dusty blue
    "quality_score": "#8FAE5D",       # dusty green
    "engagement_score": "#D0715A",    # dusty red
    "momentum_score": "#D9A441",      # dusty yellow
}
# rank within each dimension, across ALL scored publishers (not just top 10)
for d in DIMS:
    df[d + "_rank"] = df[d].rank(ascending=False, method="min").astype("Int64")

top10 = df.head(10)
top5 = top10.head(5)

# --- Plot 1: Top 10 by overall_score ---------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))
plot_order = top10.iloc[::-1]
colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(top10)))[::-1]
bars = ax.barh(plot_order["primary_publisher"], plot_order["overall_score"], color="#107c10")
for bar, val in zip(bars, plot_order["overall_score"]):
    ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Overall Score")
ax.set_title("Top 10 Publishers by Overall Score", fontsize=13, fontweight="bold")
ax.set_xlim(0, top10["overall_score"].max() * 1.15)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot1_top10_overall.png", dpi=150)
plt.close()

# --- Plot 2: Top 5 -- % contribution of each dimension (STACKED bar) -------
contrib_pct = pd.DataFrame({d: top5[d] * DIMENSION_WEIGHTS[d] for d in DIMS})
contrib_pct = contrib_pct.div(contrib_pct.sum(axis=1), axis=0) * 100
contrib_pct.index = top5["primary_publisher"]
contrib_pct = contrib_pct.iloc[::-1]  # so #1 plots on top

fig, ax = plt.subplots(figsize=(9, 5))
left = np.zeros(len(contrib_pct))
for d in DIMS:
    bars = ax.barh(contrib_pct.index, contrib_pct[d], left=left, color=COLORS[d], label=LABELS[d])
    for i, (pub, val) in enumerate(zip(contrib_pct.index, contrib_pct[d])):
        if val > 4:
            ax.text(left[i] + val / 2, i, f"{val:.0f}%", ha="center", va="center", fontsize=9, fontweight="bold", color="white")
    left += contrib_pct[d].values
ax.set_xlabel("% Contribution to Overall Score")
ax.set_xlim(0, 100)
ax.set_title("Dimension Contribution to Overall Score -- Top 5 Publishers", fontsize=13, fontweight="bold")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot2_top5_contribution.png", dpi=150, bbox_inches="tight")
plt.close()


# --- Plot 3: Top 10 by review_score (0-9) -----------------------------------
top10_review = df.dropna(subset=["review_score"]).nlargest(10, "review_score")
print("\nTop 10 publishers by review_score (0-9, zeros excluded from the average upstream):")
print(top10_review[["primary_publisher", "game_count", "review_score"]].to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 6))
plot_order = top10_review.iloc[::-1]
colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(plot_order)))[::-1]
bars = ax.barh(plot_order["primary_publisher"], plot_order["review_score"], color="#107c10")
for bar, val in zip(bars, plot_order["review_score"]):
    ax.text(val + 0.06, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", fontsize=9)
ax.set_xlabel("Review Score (0-9)")
ax.set_xlim(0, 9.5)
ax.set_title("Top 10 Publishers by Review Score", fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot4_top10_review_score.png", dpi=150)
plt.close()

# --- Plot 4: Top 10 per individual dimension (2x2 grid) --------------------
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
for ax, d in zip(axes.flat, DIMS):
    top10_dim = df.dropna(subset=[d]).nlargest(10, d).iloc[::-1]
    colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(top10_dim)))[::-1]
    bars = ax.barh(top10_dim["primary_publisher"], top10_dim[d], color="#107c10")
    for bar, val in zip(bars, top10_dim[d]):
        ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=8)
    ax.set_xlabel(f"{LABELS[d]} Score")
    ax.set_xlim(0, top10_dim[d].max() * 1.15)
    ax.set_title(f"Top 10 by {LABELS[d]}", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("Top 10 Publishers per Individual Dimension", fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot5_top10_per_dimension.png", dpi=150, bbox_inches="tight")
plt.close()




# Identify the top 3 by overall_score, excluding Xbox itself (the baseline/
# acquirer, not a target) -- labels reference rank only, not the name.
ranked = df[df["primary_publisher"] != "Xbox Game Studios"].sort_values("overall_score", ascending=False)
top5_publishers = ranked["primary_publisher"].head(5).tolist()

ACQUISITION_STEPS = [
    ("Xbox Game Studios\n(baseline)", ["Xbox Game Studios"]),
    ("+ Rank #1", ["Xbox Game Studios", top5_publishers[0]]),
    ("+ Rank #2", ["Xbox Game Studios", top5_publishers[0], top5_publishers[1]]),
    ("+ Rank #3", ["Xbox Game Studios", top5_publishers[0], top5_publishers[1], top5_publishers[2]])
   
]

# Simple average of each publisher's own avg_owners_mid -- equal-weights
# every publisher regardless of portfolio size.
labels, total_owners, total_games = [], [], []
for label, publishers in ACQUISITION_STEPS:
    subset = df[df["primary_publisher"].isin(publishers)]
    labels.append(label)
    total_owners.append((subset["avg_owners_mid"] * subset["game_count"]).sum())
    total_games.append(subset["game_count"].sum())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(labels)))

bars1 = ax1.bar(labels, total_owners, color="#107c10")
for bar, val in zip(bars1, total_owners):
    ax1.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax1.set_ylabel("Total Combined Reach (sum of owners_mid)")
ax1.set_title("Cumulative Reach", fontsize=13, fontweight="bold")
ax1.spines[["top", "right"]].set_visible(False)

bars2 = ax2.bar(labels, total_games, color="#107c10")
for bar, val in zip(bars2, total_games):
    ax2.text(bar.get_x() + bar.get_width() / 2, val, f"{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax2.set_ylabel("Total Combined Portfolio Size (game_count)")
ax2.set_title("Cumulative Game Count", fontsize=13, fontweight="bold")
ax2.spines[["top", "right"]].set_visible(False)

fig.suptitle("Scale & Reach: Cumulative Acquisition Impact", fontsize=15, fontweight="bold")
plt.tight_layout()
plt.savefig("./acquisition_reach.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Plot: Top 10 -- relative strength per dimension (grouped bars) --------
# Re-scale each dimension using ONLY the top 10's own min/max (not the full
# ~800-publisher pool). Against the full pool, all 10 finalists sit bunched
# near the top of every dimension, so differences barely show. Rescaling
# within just this group is what actually reveals who's relatively strong
# or weak at what -- this is about differentiating the finalists, not
# re-deriving the original overall_score (which is why weights don't apply
# here).
EXCLUDE_PUBLISHERS = ["PlayStation Publishing LLC"]

top10_candidates = df[~df["primary_publisher"].isin(EXCLUDE_PUBLISHERS)].nlargest(4, "overall_score")

x = np.arange(len(top10_candidates))
width = 0.2

fig, ax = plt.subplots(figsize=(15, 7))
for i, d in enumerate(DIMS):
    offset = (i - 1.5) * width
    bars = ax.bar(x + offset, top10_candidates[d], width, label=LABELS[d], color=COLORS[d])
    for bar, val in zip(bars, top10_candidates[d]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.2f}", ha="center", va="bottom", fontsize=7)

ax.set_xticks(x)
ax.set_xticklabels(top10_candidates["primary_publisher"], rotation=25, ha="right")
ax.set_ylabel("Dimension Score (0-1, scaled against all publishers)")
ax.set_title("Top 10 Acquisition Candidates -- Dimension Scores", fontsize=13, fontweight="bold")
ax.set_ylim(0, 1.15)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot6_top10_overall.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Plot 7: Cumulative revenue from acquiring top-ranked publishers -------
BASELINE = "Xbox Game Studios"
EXCLUDE_PUBLISHERS = ["PlayStation Publishing LLC"]

top3_targets = (
    df[~df["primary_publisher"].isin(EXCLUDE_PUBLISHERS + [BASELINE])]
    .nlargest(3, "overall_score")["primary_publisher"]
    .tolist()
)

ACQUISITION_STEPS = [
    (f"{BASELINE}\n(baseline)", [BASELINE]),
    ("+ Rank #1", [BASELINE, top3_targets[0]]),
    ("+ Rank #2", [BASELINE, top3_targets[0], top3_targets[1]]),
    ("+ Rank #3", [BASELINE, top3_targets[0], top3_targets[1], top3_targets[2]]),
]

# total_est_revenue is already a per-publisher SUM (not average), so
# summing it across the included publishers is a true cumulative total --
# always non-negative, so this can only go up, never dip like the earlier
# simple-average version did.
labels, cumulative_revenue = [], []
for label, publishers in ACQUISITION_STEPS:
    subset = df[df["primary_publisher"].isin(publishers)]
    labels.append(label)
    cumulative_revenue.append(subset["total_est_revenue"].sum())

fig, ax = plt.subplots(figsize=(9, 6))
colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(labels)))
bars = ax.bar(labels, cumulative_revenue, color=colors)
for bar, val in zip(bars, cumulative_revenue):
    ax.text(bar.get_x() + bar.get_width() / 2, val, f"€{val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Cumulative Estimated Revenue (EUR)")
ax.set_title("Cumulative Revenue Impact of Acquiring Top-Ranked Publishers", fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot7_cumulative_revenue.png", dpi=150, bbox_inches="tight")
plt.close()


print("\nSaved 7 plots:")
print(f"  {PLOT_DIR}/plot1_top10_overall.png")
print(f"  {PLOT_DIR}/plot2_top5_contribution.png")
print(f"  {PLOT_DIR}/plot3_top10_rank_heatmap.png")
print(f"  {PLOT_DIR}/plot4_top10_review_score.png")
print(f"  {PLOT_DIR}/plot5_top10_per_dimension.png")
print(f"  {PLOT_DIR}/plot6_top10_overall.png")
print(f"  {PLOT_DIR}/plot7_cumulative_revenue.png")
