"""
Statistical Analysis, Outlier Detection & Comparable Segmentation Module (Project 13)
Implements 8+ NumPy vectorised statistical operations and 10+ pandas analytical workflows.
"""

import numpy as np
import pandas as pd


def compute_robust_outlier_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use NumPy quantiles, IQR, and MAD (Median Absolute Deviation) to compute
    robust modified z-scores and flag extreme price_per_sqft outliers within segments.
    """
    out = df.copy()
    ppsf = out["price_per_sqft"].to_numpy(dtype=float)

    # Global NumPy percentiles & IQR
    q25, q50, q75 = np.percentile(ppsf, [25, 50, 75])
    iqr = q75 - q25
    mad = np.median(np.abs(ppsf - q50))

    # Modified Z-score using MAD (consistency constant 0.6745)
    modified_z = 0.6745 * (ppsf - q50) / (mad if mad > 0 else 1.0)
    out["modified_z_ppsf"] = np.round(modified_z, 3)
    out["is_robust_outlier"] = (np.abs(modified_z) > 3.5) | (ppsf > q75 + 1.5 * iqr) | (ppsf < q25 - 1.5 * iqr)
    return out


def build_comparable_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct comparable-property cohorts based on Property Type, Size Tier,
    and Neighbourhood Zone to control for apples-to-apples comparisons.
    """
    out = df.copy()
    area_arr = out["area_sqft"].to_numpy()
    out["size_tier"] = np.select(
        [area_arr < 1000, (area_arr >= 1000) & (area_arr < 1800), area_arr >= 1800],
        ["Compact (<1,000 sqft)", "Mid-Size (1,000-1,799 sqft)", "Large (1,800+ sqft)"],
        default="Mid-Size (1,000-1,799 sqft)",
    )
    out["comp_segment"] = (
        out["zone_type"] + " | " + out["property_type_clean"] + " | " + out["size_tier"]
    )
    # Segment-relative price index using pandas transform
    seg_median = out.groupby("comp_segment")["price_per_sqft"].transform("median")
    out["relative_price_index"] = np.round((out["price_per_sqft"] / seg_median) * 100.0, 2)
    return out


def summarize_neighbourhoods(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate neighbourhood KPIs with robust percentiles and IQR."""
    summary = (
        df.groupby(["neighbourhood_id", "neighbourhood_name", "zone_type", "transit_score", "school_rating", "median_household_income"])
        .agg(
            listing_count=("listing_id", "count"),
            median_price_usd=("price_usd", "median"),
            mean_price_usd=("price_usd", "mean"),
            median_ppsf=("price_per_sqft", "median"),
            p25_ppsf=("price_per_sqft", lambda s: np.percentile(s, 25)),
            p75_ppsf=("price_per_sqft", lambda s: np.percentile(s, 75)),
            median_area_sqft=("area_sqft", "median"),
            sale_share_pct=("record_type", lambda s: np.mean(s == "Sale") * 100.0),
        )
        .reset_index()
        .sort_values("median_ppsf", ascending=False)
    )
    summary["iqr_ppsf"] = np.round(summary["p75_ppsf"] - summary["p25_ppsf"], 2)
    for col in ["median_price_usd", "mean_price_usd", "median_ppsf", "p25_ppsf", "p75_ppsf", "sale_share_pct"]:
        summary[col] = np.round(summary[col], 2)
    return summary


def quantify_listing_vs_sale_bias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare asking Listing prices vs closed Sale prices across comparable segments
    and run sensitivity analysis excluding robust outliers.
    """
    piv = pd.pivot_table(
        df,
        values="price_per_sqft",
        index="neighbourhood_name",
        columns="record_type",
        aggfunc="median",
    ).reset_index()
    piv["listing_premium_pct"] = np.round(((piv["Listing"] - piv["Sale"]) / piv["Sale"]) * 100.0, 2)

    # Sensitivity check: median PPSF after dropping robust outliers
    inliers = df.query("not is_robust_outlier")
    inlier_sale = (
        inliers.query("record_type == 'Sale'")
        .groupby("neighbourhood_name")["price_per_sqft"]
        .median()
        .rename("Sale_Inlier_Median")
    )
    piv = piv.merge(inlier_sale, on="neighbourhood_name", how="left")
    piv["outlier_sensitivity_diff_pct"] = np.round(
        ((piv["Sale"] - piv["Sale_Inlier_Median"]) / piv["Sale_Inlier_Median"]) * 100.0, 2
    )
    return piv.sort_values("Sale", ascending=False)


def analyze_temporal_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly resampled median PPSF and 3-month rolling average by zone."""
    ts = df.set_index("transaction_date_clean").sort_index()
    monthly = (
        ts.groupby("zone_type")["price_per_sqft"]
        .resample("M")
        .median()
        .reset_index()
    )
    monthly["rolling_3m_ppsf"] = (
        monthly.groupby("zone_type")["price_per_sqft"]
        .transform(lambda s: s.rolling(3, min_periods=1).mean())
        .round(2)
    )
    return monthly


def compute_hedonic_correlations(df: pd.DataFrame) -> pd.Series:
    """Compute NumPy Pearson correlation coefficients against price_per_sqft."""
    features = ["transit_score", "school_rating", "dist_cbd_km", "median_household_income", "amenity_score", "property_age"]
    target = df["price_per_sqft"].to_numpy(dtype=float)
    corrs = {}
    for feat in features:
        arr = df[feat].to_numpy(dtype=float)
        corrs[feat] = round(float(np.corrcoef(arr, target)[0, 1]), 4)
    return pd.Series(corrs, name="pearson_r_with_ppsf").sort_values(ascending=False)
