"""
Data Cleaning, Standardisation & Validation Module (Project 13)
Handles unit conversions, currency standardisation, deduplication,
implausible value filtering, and referential join validation.
"""

import numpy as np
import pandas as pd


CURRENCY_TO_USD = {
    "USD": 1.0,
    "EUR": 1.087,        # 1 EUR = 1.087 USD
    "INR_LAKHS": 1197.6, # 1 Lakh INR (~100,000 INR) / 83.5 = 1197.60 USD
}

SQM_TO_SQFT = 10.7639


def standardize_property_types(series: pd.Series) -> pd.Series:
    """Normalize noisy property category labels into canonical categories."""
    mapping = {
        "apt": "Apartment",
        "apartment": "Apartment",
        "house": "Detached House",
        "detached house": "Detached House",
        "condo": "Condo",
        "condominium": "Condo",
        "townhouse": "Townhouse",
    }
    cleaned = series.astype(str).str.strip().str.lower()
    return cleaned.map(mapping).fillna("Other")


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse mixed ISO (YYYY-MM-DD) and European (DD/MM/YYYY) date strings."""
    parsed = pd.to_datetime(series, format="mixed", dayfirst=True, errors="coerce")
    return parsed


def clean_and_validate_properties(
    raw_df: pd.DataFrame,
    nbh_df: pd.DataFrame,
    min_area_sqft: float = 250.0,
    max_area_sqft: float = 15000.0,
    min_price_usd: float = 40000.0,
    max_price_usd: float = 15000000.0,
) -> tuple[pd.DataFrame, dict]:
    """
    Execute full cleaning, feature engineering, outlier filtering, and join audit.
    Returns (cleaned_merged_df, audit_report_dict).
    """
    audit = {
        "raw_row_count": int(len(raw_df)),
        "unique_listing_ids_raw": int(raw_df["listing_id"].nunique()),
    }

    df = raw_df.copy()

    # 1. Deduplication on primary grain (listing_id)
    dup_count = int(df.duplicated(subset=["listing_id"]).sum())
    df = df.drop_duplicates(subset=["listing_id"], keep="first").reset_index(drop=True)
    audit["duplicates_removed"] = dup_count

    # 2. Standardize property categories & dates
    df["property_type_clean"] = standardize_property_types(df["property_type"])
    df["transaction_date_clean"] = parse_mixed_dates(df["transaction_date"])
    audit["invalid_dates_dropped"] = int(df["transaction_date_clean"].isna().sum())
    df = df.dropna(subset=["transaction_date_clean"]).copy()

    # 3. Standardize currency to USD & area to sqft using NumPy vectorised operations
    fx_multiplier = df["currency"].map(CURRENCY_TO_USD).to_numpy(dtype=float)
    df["price_usd"] = np.round(df["price"].to_numpy(dtype=float) * fx_multiplier, 2)

    is_sqm = (df["area_unit"].str.lower() == "sqm").to_numpy()
    raw_area_arr = df["area"].to_numpy(dtype=float)
    df["area_sqft"] = np.round(np.where(is_sqm, raw_area_arr * SQM_TO_SQFT, raw_area_arr), 2)

    # 4. Filter implausible physical area and price records
    valid_mask = (
        (df["area_sqft"] >= min_area_sqft)
        & (df["area_sqft"] <= max_area_sqft)
        & (df["price_usd"] >= min_price_usd)
        & (df["price_usd"] <= max_price_usd)
    )
    audit["implausible_records_removed"] = int((~valid_mask).sum())
    df = df.loc[valid_mask].copy()

    # 5. Impute minor missing values in secondary attributes using group medians
    df["bathrooms"] = df["bathrooms"].fillna(
        df.groupby("bedrooms")["bathrooms"].transform("median")
    )
    df["year_built"] = df["year_built"].fillna(
        df.groupby("property_type_clean")["year_built"].transform("median")
    ).astype(int)

    # 6. Engineer core analytical features (Price per SqFt, Property Age, Amenity Score)
    df["price_per_sqft"] = np.round(df["price_usd"] / df["area_sqft"], 2)
    df["property_age"] = np.maximum(0, df["transaction_date_clean"].dt.year - df["year_built"])
    df["amenity_score"] = (
        df["has_parking"].to_numpy() * 1
        + df["has_gym_pool"].to_numpy() * 2
        + df["renovated"].to_numpy() * 2
    )
    df["year_quarter"] = df["transaction_date_clean"].dt.to_period("Q").astype(str)
    df["year_month"] = df["transaction_date_clean"].dt.to_period("M").astype(str)

    # 7. Validate merge cardinality and unmatched neighbourhood keys (Many-to-One)
    assert nbh_df["neighbourhood_id"].is_unique, "Neighbourhood key must be unique!"
    merged = pd.merge(
        df,
        nbh_df,
        on="neighbourhood_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    unmatched_count = int((merged["_merge"] == "left_only").sum())
    audit["unmatched_neighbourhood_rows"] = unmatched_count
    merged = merged.loc[merged["_merge"] == "both"].drop(columns=["_merge"]).reset_index(drop=True)
    audit["final_clean_row_count"] = int(len(merged))

    return merged, audit
