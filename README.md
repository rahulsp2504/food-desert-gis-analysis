## Project Overview

### The Problem
Food deserts are census tracts where residents are low income AND live more than 
1 mile from a grocery store (urban) or 10 miles (rural), per USDA definition. 
Understanding where these areas exist and who lives in them is critical for 
public health policy, urban planning, and business decisions.

### Data Source
**USDA Economic Research Service — Food Access Research Atlas 2019**
- 72,531 census tracts across the US (147 fields)
- Filtered to California: 8,024 census tracts
- Key fields: LILATracts_1And10, PovertyRate, MedianFamilyIncome, 
  TractHUNV, TractSNAP, TractBlack, TractHispanic

### Data Engineering Pipeline

**1. Load & Filter**
- Loaded 72,531 rows × 147 columns
- Filtered to California — 8,024 tracts
- Dropped unpopulated tracts (Pop2010 = 0)

**2. Feature Engineering**
Created normalized rate fields not present in raw data:
- `NoVehicleRate` = TractHUNV / Pop2010 × 100
- `SNAPRate` = TractSNAP / Pop2010 × 100
- `PctHispanic` = TractHispanic / Pop2010 × 100
- `PctBlack` = TractBlack / Pop2010 × 100
- `PctSeniors` = TractSeniors / Pop2010 × 100

**3. Comparative Analysis**
Split into food desert vs non-food desert groups and compared:

| Metric | Food Desert | Non-Desert |
|---|---|---|
| Avg Poverty Rate | 22.4% | 14.0% |
| Avg Median Income | $54,233 | $89,817 |
| Avg SNAP Rate | 5.2% | 3.0% |
| Avg % Hispanic | 43.8% | 35.9% |

**4. Geometry Merge**
- Downloaded 65,885 California census tract boundaries from Census Bureau TIGER API
- Matched to food access data using 11-digit FIPS code (99.2% match rate)
- Merged into GeoJSON with geometry + attributes

**5. Publish to ArcGIS Online**
- Uploaded GeoJSON via ArcGIS Python API with OAuth2 authentication
- Published as hosted feature layer
- Shared publicly for dashboard and Experience Builder consumption

### Key Findings
- **536 food desert tracts** in California — 6.7% of all tracts
- **2.67 million people** live in food deserts
- Food desert tracts have **60% higher poverty rates** (22.4% vs 14.0%)
- **$35K income gap** — $54K vs $89K median family income
- **Hispanic communities disproportionately affected** — 43.8% vs 35.9%
- **SNAP dependency nearly double** — 5.2% vs 3.0%
- Distance to stores is primary barrier — no vehicle rates are similar, 
  suggesting store placement matters more than transit improvement

## Live Products (open in new tab)
- Dashboard: `https://www.arcgis.com/apps/dashboards/26d4ce294f764a7e8ec24356e19b5124`
- Experience Builder: `https://experience.arcgis.com/experience/9ddbdcd5dbe5410c8c47a0dc6289613d`

## Screenshots
![Dashboard](food_desert_dashboard.png)
![Experience Builder](ExperienceBuilder.png)

### Business Applications
1. **Grocery/food retail** — identify underserved markets for new store locations
2. **Food bank logistics** — optimize delivery routes to food desert communities
3. **Fleet operators** — support clients in food distribution with spatial gap analysis
4. **Policy** — identify communities qualifying for federal food access grants
