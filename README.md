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

## Live Products
- [🗺️ Interactive Dashboard](https://www.arcgis.com/apps/dashboards/26d4ce294f764a7e8ec24356e19b5124)
- [🔍 Experience Builder App](https://experience.arcgis.com/experience/9ddbdcd5dbe5410c8c47a0dc6289613d)

## Key Findings
- 536 food desert census tracts in California
- 2.7 million people live in food deserts
- Food desert tracts have 60% higher poverty rates (22.4% vs 14.0%)
- Median family income gap: $54K vs $89K
- Hispanic communities disproportionately affected (43.8% vs 35.9%)
- SNAP dependency nearly double in food desert tracts (5.2% vs 3.0%)
