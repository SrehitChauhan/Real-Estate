"""
Visualization & Map-Ready Export Module (Project 13)
Generates 5 publication-grade figures saved to output/figures/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def generate_all_charts(
    df: pd.DataFrame,
    nbh_summary: pd.DataFrame,
    bias_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    corr_series: pd.Series,
    fig_dir: str,
) -> list[str]:
    """Generate and save all 5 required analytical charts."""
    os.makedirs(fig_dir, exist_ok=True)
    saved_paths = []

    # Figure 1: Price per SqFt Distribution by Neighbourhood (Boxplot + Median annotations)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    order = nbh_summary["neighbourhood_name"].tolist()
    data_groups = [df.loc[df["neighbourhood_name"] == n, "price_per_sqft"].values for n in order]
    bp = ax.boxplot(data_groups, labels=order, patch_artist=True, showfliers=True,
                    flierprops=dict(marker="o", markersize=3, alpha=0.45, markerfacecolor="#d95f02"))
    colors = ["#1b9e77", "#2b8cbe", "#7570b3", "#66a61e", "#e6ab02", "#a6761d"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_title("Fig 1. Price per SqFt Distribution Across Neighbourhoods (USD/sqft)")
    ax.set_ylabel("Price per SqFt (USD)")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    p1 = os.path.join(fig_dir, "fig1_neighbourhood_ppsf_distribution.png")
    fig.savefig(p1)
    plt.close(fig)
    saved_paths.append(p1)

    # Figure 2: Listing vs. Closed Sale Median Price per SqFt (Listing Bias Check)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    x = np.arange(len(bias_df))
    width = 0.36
    ax.bar(x - width / 2, bias_df["Sale"], width, label="Closed Sale (Median)", color="#2b8cbe")
    ax.bar(x + width / 2, bias_df["Listing"], width, label="Active Listing (Median)", color="#e34a33")
    for idx, row in bias_df.reset_index(drop=True).iterrows():
        ax.text(idx, max(row["Sale"], row["Listing"]) + 8, f"+{row['listing_premium_pct']:.1f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#b30000")
    ax.set_xticks(x)
    ax.set_xticklabels(bias_df["neighbourhood_name"], rotation=20)
    ax.set_ylabel("Median Price per SqFt (USD)")
    ax.set_title("Fig 2. Listing-vs-Sale Asking Bias by Neighbourhood (USD/sqft)")
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    p2 = os.path.join(fig_dir, "fig2_listing_vs_sale_bias.png")
    fig.savefig(p2)
    plt.close(fig)
    saved_paths.append(p2)

    # Figure 3: Comparable Property Matrix (Property Type x Size Tier Median PPSF)
    comp_piv = df.pivot_table(
        values="price_per_sqft", index="property_type_clean", columns="size_tier", aggfunc="median"
    )
    col_order = [c for c in ["Compact (<1,000 sqft)", "Mid-Size (1,000-1,799 sqft)", "Large (1,800+ sqft)"] if c in comp_piv.columns]
    comp_piv = comp_piv[col_order]
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(comp_piv.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(np.arange(len(comp_piv.columns)))
    ax.set_xticklabels(comp_piv.columns, rotation=15)
    ax.set_yticks(np.arange(len(comp_piv.index)))
    ax.set_yticklabels(comp_piv.index)
    for i in range(len(comp_piv.index)):
        for j in range(len(comp_piv.columns)):
            val = comp_piv.values[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"${val:,.0f}", ha="center", va="center", color="black", fontweight="bold")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Median Price per SqFt (USD)")
    ax.set_title("Fig 3. Comparable Segments: Median PPSF by Property Type & Size Tier")
    p3 = os.path.join(fig_dir, "fig3_comparable_segments_heatmap.png")
    fig.savefig(p3)
    plt.close(fig)
    saved_paths.append(p3)

    # Figure 4: 3-Month Rolling Median Price per SqFt Trend by Urban Zone (2024-2025)
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    for zone, grp in monthly_df.groupby("zone_type"):
        ax.plot(grp["transaction_date_clean"], grp["rolling_3m_ppsf"], marker="o", markersize=3.5, linewidth=2, label=zone)
    ax.set_title("Fig 4. 3-Month Rolling Median Price per SqFt by Zone Type (2024–2025)")
    ax.set_ylabel("3-Month Rolling Median PPSF (USD)")
    ax.set_xlabel("Transaction Month")
    ax.legend(title="Zone Type", frameon=False, ncol=2)
    ax.grid(True, linestyle="--", alpha=0.4)
    p4 = os.path.join(fig_dir, "fig4_temporal_rolling_trends.png")
    fig.savefig(p4)
    plt.close(fig)
    saved_paths.append(p4)

    # Figure 5: Geospatial Map-Ready Scatter Plot (Lat/Lon coloured by PPSF)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    sc = ax.scatter(
        df["longitude"], df["latitude"],
        c=df["price_per_sqft"], cmap="viridis", alpha=0.75, s=28, edgecolors="none"
    )
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Price per SqFt (USD)")
    for _, row in df.groupby("neighbourhood_name")[["longitude", "latitude"]].median().iterrows():
        ax.annotate(row.name, (row["longitude"], row["latitude"]), fontsize=8.5, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85))
    ax.set_title("Fig 5. Spatial Price Gradient Across Neighbourhood Coordinates")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle="--", alpha=0.35)
    p5 = os.path.join(fig_dir, "fig5_spatial_price_map.png")
    fig.savefig(p5)
    plt.close(fig)
    saved_paths.append(p5)

    return saved_paths
