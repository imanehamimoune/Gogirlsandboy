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

Also generates 3 plots in the same run:
  1. Top 10 publishers by overall_score (bar chart)
  2. Top 5 publishers -- % contribution of each dimension (donut charts)
  3. Top 10 publishers -- rank in each individual dimension out of all
     scored publishers (heatmap)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SRC = "data/feature_analysis/publisher_features.csv"
OUT = "data/feature_analysis/publisher_scores.csv"
PLOT_DIR = "src/feature_engineering/"

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
df[final_cols].to_csv(OUT, index=False)
print(f"\nSaved: {OUT}  shape={df[final_cols].shape}")

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
COLORS = {"scale_reach_score": "#4C72B0", "quality_score": "#55A868",
          "engagement_score": "#C44E52", "momentum_score": "#8172B2"}

# rank within each dimension, across ALL scored publishers (not just top 10)
for d in DIMS:
    df[d + "_rank"] = df[d].rank(ascending=False, method="min").astype("Int64")

top10 = df.head(10)
top4 = top10.head(4)

# --- Plot 1: Top 10 by overall_score ---------------------------------------
fig, ax = plt.subplots(figsize=(9, 6))
plot_order = top10.iloc[::-1]
colors = plt.cm.viridis(np.linspace(0.85, 0.15, len(top10)))[::-1]
bars = ax.barh(plot_order["primary_publisher"], plot_order["overall_score"], color=colors)
for bar, val in zip(bars, plot_order["overall_score"]):
    ax.text(val + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}", va="center", fontsize=9)
ax.set_xlabel("Overall Score")
ax.set_title("Top 10 Publishers by Overall Score", fontsize=13, fontweight="bold")
ax.set_xlim(0, top10["overall_score"].max() * 1.15)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig(f"{PLOT_DIR}/plot1_top10_overall.png", dpi=150)
plt.close()

# --- Plot 2: Top 4 -- % contribution of each dimension (stacked bar) -------

fig, ax = plt.subplots(figsize=(12, 6))

publishers = top4["primary_publisher"].tolist()

# Calculate percentage contribution for each publisher
pct_data = []

for _, row in top4.iterrows():
    contrib = {
        d: row[d] * DIMENSION_WEIGHTS[d]
        for d in DIMS
    }

    total = sum(contrib.values())

    pct_data.append({
        d: (contrib[d] / total * 100 if total else 0)
        for d in DIMS
    })

# Plot stacked bars
bottom = np.zeros(len(top4))

for d in DIMS:
    values = np.array([p[d] for p in pct_data])

    bars = ax.bar(
        publishers,
        values,
        bottom=bottom,
        color=COLORS[d],
        label=LABELS[d],
    )

    # Percentage labels
    for bar, value, base in zip(bars, values, bottom):
        if value > 4:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                base + value / 2,
                f"{value:.0f}%",
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="white",
            )

    bottom += values


# --- Formatting ------------------------------------------------------------

ax.set_title(
    "Dimension Contribution to Overall Score -- Top 4 Publishers",
    fontsize=13,
    fontweight="bold",
)

ax.set_ylabel("Contribution (%)")
ax.set_ylim(0, 100)

ax.legend(
    title="Dimension",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.15),
    ncol=len(DIMS),
    frameon=False,
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.xticks(rotation=20, ha="right")

plt.tight_layout()

plt.savefig(
    f"{PLOT_DIR}/plot2_top4_contribution.png",
    dpi=150,
    bbox_inches="tight",
)

plt.close()

# --- Plot 3: Top 4 -- rank across dimensions (bump chart) -----------------

rank_cols = [f"{d}_rank" for d in DIMS]

rank_matrix = (
    top4
    .set_index("primary_publisher")[rank_cols]
    .astype(float)
)

rank_matrix.columns = DIMS

fig, ax = plt.subplots(figsize=(11, 7))

x = np.arange(len(DIMS))

# Plot one line per publisher
for publisher, row in rank_matrix.iterrows():

    ranks = row.values

    ax.plot(
        x,
        ranks,
        marker="o",
        markersize=7,
        linewidth=1.8,
        alpha=0.75,
    )

    # Publisher name on the right
    ax.text(
        x[-1] + 0.12,
        ranks[-1],
        publisher,
        va="center",
        fontsize=8,
    )

# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------

ax.set_xticks(x)
ax.set_xticklabels(
    [LABELS[d] for d in DIMS],
    fontsize=10,
    fontweight="bold",
)

# Rank 1 should be at the top
ax.invert_yaxis()

ax.set_ylabel("Rank (1 = best)")

ax.set_title(
    "How Top 4 Publishers Rank Across Dimensions",
    fontsize=13,
    fontweight="bold",
    pad=15,
)

# Vertical guides for dimensions
ax.grid(
    axis="x",
    linestyle="--",
    alpha=0.25,
)

# Clean appearance
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Extra space for publisher labels
ax.set_xlim(-0.2, len(DIMS) - 1 + 1.2)

plt.tight_layout()

plt.savefig(
    f"{PLOT_DIR}/plot3_top4_rank_bump.png",
    dpi=150,
    bbox_inches="tight",
)

plt.close()

print("\nSaved 3 plots:")
print(f"  {PLOT_DIR}/plot1_top10_overall.png")
print(f"  {PLOT_DIR}/plot2_top4_contribution.png")
print(f"  {PLOT_DIR}/plot3_top4_rank_bump.png")
