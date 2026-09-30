# JanSetu AI - Data Layer

This directory contains the data layer for JanSetu AI. It includes realistic district-level reference data for 50+ Indian districts across various states, state-level census population statistics, and synthetic complaint datasets representing civic infrastructure issues.

## Files Generated:

1. **`generate_synthetic.py`**: A Python script to generate 500 realistic synthetic citizen infrastructure feedback requests across India. No external API calls are required; all text uses native localized templates spanning 10 languages (Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Odia, Punjabi) across 7 categories (ROADS, WATER, ELECTRICITY, HEALTHCARE, EDUCATION, SANITATION, DIGITAL).
2. **`synthetic_requests.json`**: The output of `generate_synthetic.py` (after execution). It contains entries properly tagged with `data_type: SYNTHETIC` and transliterated/native complaint text.
3. **`districts.csv`**: District reference data (population estimates, geographic coordinates, overall infrastructure indices). Data is approximate and based on public/census domains.
4. **`infrastructure_index.csv`**: A detailed breakdown of the infrastructure scores across different sectors (roads, water, electricity, healthcare, etc.) for the districts. Scores range from 0.0 to 1.0.
5. **`census_population.csv`**: State-level demographic data across all 28 states and 8 UTs (urban vs rural populations, literacy rate, district count). 

*Note: All data provided is synthetic or approximate reference data generated for hackathon scaffolding and testing purposes.*
