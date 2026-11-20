# Project 13: Real Estate Price & Neighbourhood Intelligence

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/NumPy-Vectorised-013243.svg)](https://numpy.org/)
[![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)

A reproducible, modular data-analysis pipeline built with **Python, NumPy, and pandas** to evaluate residential real estate pricing, neighbourhood socioeconomic drivers, comparable property segments, and listing-vs-sale asking bias.

## Repository Structure
```text
Real_Estate_Price_Neighbourhood_Intelligence/
├── srs/                         # Software Requirements Specification & Data Dictionary
│   ├── SRS_Document.md
│   └── data_dictionary.md
├── src/                         # Modular Python source code
│   ├── __init__.py
│   ├── data_cleaning.py         # Unit/currency standardisation, deduplication & join validation
│   ├── analysis.py              # NumPy MAD outliers, comparable segments & sensitivity checks
│   ├── visualization.py         # Publication-grade Matplotlib chart generator
│   └── main.py                  # End-to-end CLI pipeline runner
├── data/
│   ├── raw/                     # Raw multi-currency property listings & neighbourhood indicators
│   └── processed/               # Cleaned, validated master analytical dataset
├── notebooks/
│   └── project13_analysis.ipynb # Interactive Jupyter Notebook walkthrough
├── output/
│   ├── figures/                 # 5 exported high-resolution analytical charts (.png)
│   ├── tables/                  # Neighbourhood summaries, sensitivity tables & map-ready CSV
│   └── reports/                 # Market insight report & JSON execution audit
├── requirements.txt
├── .gitignore
└── README.md
```

## Quickstart (Reproducible Execution)

1. **Clone the repository and install dependencies:**
   ```bash
   git clone <your-github-repo-url>
   cd Real_Estate_Price_Neighbourhood_Intelligence
   pip install -r requirements.txt
   ```

2. **Run the complete end-to-end pipeline:**
   ```bash
   python -m src.main
   ```

3. **Explore interactively via Jupyter Notebook:**
   ```bash
   jupyter notebook notebooks/project13_analysis.ipynb
   ```

## Key Technical Highlights
- **Data Quality & Referential Validation**: Standardises `USD`/`EUR`/`INR_LAKHS` currencies and `sqft`/`sqm` floor areas, removes duplicate `listing_id` entries, filters implausible values, and validates `many_to_one` joins (`NBH_99` audit).
- **NumPy Vectorised Computation**: Uses `np.percentile`, `np.median`, `np.abs`, `np.where`, `np.select`, `np.corrcoef`, `np.round`, and boolean masking for Modified Z-score (`MAD`) outlier detection.
- **pandas Analytical Workflows**: Uses `groupby`, `agg`, `merge(validate=...)`, `pivot_table`, `transform`, `resample`, `rolling`, `query`, and `sort_values`.
