"""
End-to-End Reproducible Pipeline Runner for Project 13:
Real Estate Price & Neighbourhood Intelligence
"""

import os
import json
import pandas as pd

from src.data_cleaning import clean_and_validate_properties
from src.analysis import (
    compute_robust_outlier_flags,
    build_comparable_segments,
    summarize_neighbourhoods,
    quantify_listing_vs_sale_bias,
    analyze_temporal_trends,
    compute_hedonic_correlations,
)
from src.visualization import generate_all_charts


def run_pipeline(base_path: str = ".") -> None:
    raw_prop_path = os.path.join(base_path, "data", "raw", "property_listings_raw.csv")
    raw_nbh_path = os.path.join(base_path, "data", "raw", "neighbourhood_indicators.csv")

    processed_dir = os.path.join(base_path, "data", "processed")
    tables_dir = os.path.join(base_path, "output", "tables")
    figures_dir = os.path.join(base_path, "output", "figures")
    reports_dir = os.path.join(base_path, "output", "reports")

    for d in [processed_dir, tables_dir, figures_dir, reports_dir]:
        os.makedirs(d, exist_ok=True)

    # Step 1: Load raw data
    raw_df = pd.read_csv(raw_prop_path)
    nbh_df = pd.read_csv(raw_nbh_path)

    # Step 2: Clean, standardize units/currencies, validate join cardinality
    clean_df, audit = clean_and_validate_properties(raw_df, nbh_df)

    # Step 3: Robust outlier detection & comparable segment engineering
    clean_df = compute_robust_outlier_flags(clean_df)
    clean_df = build_comparable_segments(clean_df)

    # Save cleaned master table & map-ready GeoJSON-like CSV export
    clean_df.to_csv(os.path.join(processed_dir, "clean_properties.csv"), index=False)
    map_cols = [
        "listing_id", "neighbourhood_id", "neighbourhood_name", "zone_type",
        "property_type_clean", "size_tier", "record_type", "price_usd",
        "area_sqft", "price_per_sqft", "relative_price_index", "latitude", "longitude"
    ]
    clean_df[map_cols].to_csv(os.path.join(tables_dir, "map_ready_properties.csv"), index=False)

    # Step 4: Analytical aggregations & sensitivity checks
    nbh_summary = summarize_neighbourhoods(clean_df)
    bias_df = quantify_listing_vs_sale_bias(clean_df)
    monthly_df = analyze_temporal_trends(clean_df)
    corrs = compute_hedonic_correlations(clean_df)

    nbh_summary.to_csv(os.path.join(tables_dir, "neighbourhood_summary.csv"), index=False)
    bias_df.to_csv(os.path.join(tables_dir, "listing_vs_sale_bias_sensitivity.csv"), index=False)
    monthly_df.to_csv(os.path.join(tables_dir, "monthly_zone_trends.csv"), index=False)
    corrs.to_frame().to_csv(os.path.join(tables_dir, "hedonic_correlations.csv"))

    # Step 5: Generate all 5 charts
    saved_figs = generate_all_charts(clean_df, nbh_summary, bias_df, monthly_df, corrs, figures_dir)

    # Step 6: Save execution audit JSON
    audit["robust_outliers_flagged"] = int(clean_df["is_robust_outlier"].sum())
    audit["generated_figures"] = [os.path.basename(p) for p in saved_figs]
    with open(os.path.join(reports_dir, "pipeline_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)

    print("Pipeline completed successfully!")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    run_pipeline(".")
