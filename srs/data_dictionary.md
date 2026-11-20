# Data Dictionary & Provenance

## Dataset Provenance & Licence
- **Source**: Documented Synthetic Real Estate & Neighbourhood Benchmark Dataset (`data/raw/`), engineered specifically to mirror multi-currency, multi-unit municipal property registries and neighbourhood census indicators for reproducible offline execution.
- **Licence**: MIT License (open for educational, portfolio, and analytical reuse).

## Table 1: `property_listings_raw.csv` (1,268 raw rows -> 1,241 clean rows)
| Column | Type | Description | Cleaning / Validation Rule |
| :--- | :--- | :--- | :--- |
| `listing_id` | String | Primary key (`PROP_10000`–`PROP_11249`) | Deduplicated (`keep='first'`, 18 removed) |
| `neighbourhood_id` | String | Foreign key to neighbourhood table | Validated many-to-one (`4` unmatched `NBH_99` dropped) |
| `property_type` | String | Raw property category (`apt`, `HOUSE `, etc.) | Mapped to `Apartment`, `Condo`, `Townhouse`, `Detached House` |
| `record_type` | String | `Sale` (closed) vs `Listing` (asking) | Used to quantify asking-price bias |
| `transaction_date` | String | Mixed ISO and `DD/MM/YYYY` dates | Parsed via `pd.to_datetime(..., format='mixed', dayfirst=True)` |
| `price` / `currency` | Float/Str | Raw price in `USD`, `EUR`, or `INR_LAKHS` | Standardized to `price_usd` (`$40k`–`$15M` valid range) |
| `area` / `area_unit` | Float/Str | Floor area in `sqft` or `sqm` | Standardized to `area_sqft` (`250`–`15,000` valid range) |
| `bedrooms` / `bathrooms` | Int/Float | Room counts | Missing `bathrooms` imputed via bedroom-group median |
| `year_built` | Float/Int | Construction year | Missing values imputed via property-type median |
| `has_parking`, `has_gym_pool`, `renovated` | Binary | Property amenities (`0`/`1`) | Combined into weighted `amenity_score` (`0`–`5`) |
| `latitude` / `longitude` | Float | WGS84 decimal coordinates | Retained for geospatial map-ready output |

## Table 2: `neighbourhood_indicators.csv` (6 neighbourhoods)
| Column | Type | Description |
| :--- | :--- | :--- |
| `neighbourhood_id` | String | Unique neighbourhood primary key (`NBH_01`–`NBH_06`) |
| `neighbourhood_name` | String | Canonical neighbourhood name |
| `zone_type` | String | Urban classification (`Urban Core`, `Waterfront`, `Suburban`, `Mixed-Use`, `Transitioning`) |
| `transit_score` | Float | Public transit accessibility index (`0`–`10`) |
| `school_rating` | Float | Public school quality index (`0`–`10`) |
| `dist_cbd_km` | Float | Distance to Central Business District in kilometers |
| `median_household_income` | Integer | Neighbourhood annual median household income (USD) |
