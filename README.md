# US Food Desert Analysis — ArcGIS Python Pipeline

Automated data pipeline analyzing food access disparities 
across 72,531 US census tracts using USDA Food Access 
Research Atlas 2019 data.

## What This Does
- Authenticates to ArcGIS Online via OAuth2 (SSO compatible)
- Loads and cleans 72,531 census tract records (147 fields)
- Engineers features: poverty rate, vehicle access, SNAP 
  dependency, demographic breakdowns
- Aggregates to state level for comparative analysis
- Publishes hosted feature layer to ArcGIS Online via API

## Key Findings
- X% of US census tracts qualify as food deserts
- Food desert tracts have 2x higher poverty rates
- No-vehicle households are 3x more common in food deserts
- Built interactive dashboard and Experience Builder app
  on top of the published layer

## Tech Stack
- Python (pandas, numpy, requests)
- ArcGIS API for Python
- ArcGIS Online (Dashboard, Experience Builder, Story Maps)
- Data: USDA ERS Food Access Research Atlas 2019

## Setup
1. Install: `pip install arcgis pandas openpyxl`
2. Register app at your ArcGIS Online org to get Client ID
3. Download data from USDA ERS website
4. Run `food_desert_analysis.py`

## Files
- `food_desert_analysis.py` — main pipeline
- `food_access_clean.csv` — cleaned output (72K rows)
- `state_food_access_stats.csv` — state-level aggregation
