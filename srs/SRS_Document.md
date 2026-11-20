# Software Requirements Specification (SRS)
## Project 13: Real Estate Price & Neighbourhood Intelligence

### 1. Problem Framing & Success Criteria
- **Objective**: Explain property price variation across urban and suburban neighbourhoods, quantify listing-vs-sale asking bias, establish comparable-property valuation benchmarks, and evaluate sensitivity to extreme outliers.
- **Analytical Grain**: One unique property record (`listing_id`) representing either a closed transaction (`Sale`) or an active asking price (`Listing`) between January 2024 and December 2025, enriched via a validated many-to-one join with neighbourhood-level socioeconomic indicators (`neighbourhood_id`).
- **Measurable Success Criteria**:
  1. 100% deduplication of primary listing keys and full unit/currency normalization (`USD`, `sqft`).
  2. Referential integrity audit logging exact unmatched foreign keys (`NBH_99`) prior to exclusion.
  3. Execution of >=8 vectorised NumPy statistical operations and >=10 pandas analytical transformations.
  4. Generation of >=5 publication-ready figures, map-ready coordinate tables, and >=8 evidence-backed findings.

### 2. Functional Requirements
- **FR-1 Data Ingestion & Standardisation (`src/data_cleaning.py`)**: Convert EUR and INR Lakhs to USD; convert square meters (`sqm`) to square feet (`sqft`); standardize messy property labels (`apt`, `HOUSE `, `condominium`) and mixed date formats (`YYYY-MM-DD`, `DD/MM/YYYY`).
- **FR-2 Data Quality & Join Audit**: Drop exact `listing_id` duplicates, filter implausible physical dimensions (`area_sqft < 250` or `> 15,000`) and prices (`< $40,000` or `> $15,000,000`), and enforce `validate="many_to_one"` during neighbourhood merges.
- **FR-3 Robust Statistical & Comparable Analysis (`src/analysis.py`)**: Compute Price per SqFt (`PPSF`), Modified Z-Scores via Median Absolute Deviation (`MAD`), IQR bounds, comparable segments (`zone_type | property_type | size_tier`), listing-vs-sale asking premiums, and 3-month rolling trends.
- **FR-4 Reproducible Reporting & Export (`src/visualization.py`, `src/main.py`)**: Export cleaned datasets, summary CSVs, geospatial map-ready tables, and 5 high-DPI PNG figures in a single command (`python -m src.main`).

### 3. Non-Functional Requirements
- **Reproducibility**: Deterministic random seed (`42`), zero hardcoded local machine paths, clean top-to-bottom execution in a fresh Python 3.10+ environment using `requirements.txt`.
- **Modularity**: Separation of concerns across `srs/`, `src/`, `data/`, `notebooks/`, and `output/`.
