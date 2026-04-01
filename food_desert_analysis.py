# ============================================================
# US Food Desert Analysis — ArcGIS Python API
# Author: Rahul Sharad Pandit
# Description: Automated data pipeline for USDA Food Access
#              Research Atlas — cleans, analyzes, and publishes
#              72,531 census tract records to ArcGIS Online
# ============================================================

# ── 1. Install & Imports ────────────────────────────────────
# !pip install arcgis -q

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
import numpy as np
import json
import requests
import warnings
warnings.filterwarnings("ignore")

# ── 2. Authentication ────────────────────────────────────────
# Uses OAuth2 for university SSO accounts
# Replace with your organization URL and Client ID
# To get Client ID: uci.maps.arcgis.com → Content → New Item
# → Application → Register → Add redirect URI:
# urn:ietf:wg:oauth:2.0:oob

UCI_URL    = "https://ucirvine.maps.arcgis.com"
CLIENT_ID  = "YOUR_CLIENT_ID_HERE"

gis = GIS(UCI_URL, client_id=CLIENT_ID)
print(f"✓ Authenticated as: {gis.users.me.username}")

# ── 3. Load Raw Data ─────────────────────────────────────────
# Download from:
# https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data
# File: DataDownload2019.xlsx (~80MB)

print("\n── Loading USDA Food Access Research Atlas 2019...")
df = pd.read_excel(
    "DataDownload2019.xlsx",
    sheet_name="Food Access Research Atlas"
)
print(f"✓ Loaded {len(df):,} census tracts | {df.shape[1]} fields")

# ── 4. Clean & Feature Engineering ──────────────────────────
print("\n── Cleaning and engineering features...")

# Drop unpopulated tracts
df = df[df['Pop2010'] > 0].copy()

# Primary food desert flag (low income + low access at 1mi urban / 10mi rural)
df['FoodDesert'] = df['LILATracts_1And10'].fillna(0).astype(int)

# Core demographic & economic fields
df['PovertyRate']        = df['PovertyRate'].fillna(0).round(2)
df['MedianFamilyIncome'] = df['MedianFamilyIncome'].fillna(0).round(0)

# Derived rates (per 100 people)
df['NoVehicleRate'] = (df['TractHUNV']    / df['Pop2010'] * 100).fillna(0).round(2)
df['SNAPRate']      = (df['TractSNAP']    / df['Pop2010'] * 100).fillna(0).round(2)
df['PctBlack']      = (df['TractBlack']   / df['Pop2010'] * 100).fillna(0).round(2)
df['PctHispanic']   = (df['TractHispanic']/ df['Pop2010'] * 100).fillna(0).round(2)
df['PctSeniors']    = (df['TractSeniors'] / df['Pop2010'] * 100).fillna(0).round(2)
df['PctKids']       = (df['TractKids']    / df['Pop2010'] * 100).fillna(0).round(2)

# Format census tract ID with leading zeros (11 digits)
df['CensusTract'] = df['CensusTract'].astype(str).str.zfill(11)

print(f"✓ Cleaned {len(df):,} tracts")
print(f"✓ Food desert tracts: {df['FoodDesert'].sum():,.0f} "
      f"({df['FoodDesert'].mean()*100:.1f}% of all tracts)")
print(f"✓ Population in food deserts: "
      f"{df[df['FoodDesert']==1]['Pop2010'].sum():,}")

# ── 5. Summary Statistics ────────────────────────────────────
print("\n── Computing summary statistics...")

desert     = df[df['FoodDesert'] == 1]
non_desert = df[df['FoodDesert'] == 0]

stats = {
    "metric": [
        "Avg Poverty Rate (%)",
        "Avg Median Income ($)",
        "Avg No Vehicle Rate (%)",
        "Avg SNAP Rate (%)",
        "Avg % Black",
        "Avg % Hispanic"
    ],
    "food_desert": [
        f"{desert['PovertyRate'].mean():.1f}",
        f"{desert['MedianFamilyIncome'].mean():,.0f}",
        f"{desert['NoVehicleRate'].mean():.1f}",
        f"{desert['SNAPRate'].mean():.1f}",
        f"{desert['PctBlack'].mean():.1f}",
        f"{desert['PctHispanic'].mean():.1f}"
    ],
    "non_food_desert": [
        f"{non_desert['PovertyRate'].mean():.1f}",
        f"{non_desert['MedianFamilyIncome'].mean():,.0f}",
        f"{non_desert['NoVehicleRate'].mean():.1f}",
        f"{non_desert['SNAPRate'].mean():.1f}",
        f"{non_desert['PctBlack'].mean():.1f}",
        f"{non_desert['PctHispanic'].mean():.1f}"
    ]
}

stats_df = pd.DataFrame(stats)
print("\nFood Desert vs Non-Food Desert Comparison:")
print(stats_df.to_string(index=False))

# ── 6. State-Level Aggregation ───────────────────────────────
print("\n── Aggregating by state...")

state_stats = df.groupby('State').agg(
    TotalTracts       = ('CensusTract', 'count'),
    FoodDesertTracts  = ('FoodDesert', 'sum'),
    TotalPopulation   = ('Pop2010', 'sum'),
    AvgPovertyRate    = ('PovertyRate', 'mean'),
    AvgIncome         = ('MedianFamilyIncome', 'mean'),
    AvgNoVehicleRate  = ('NoVehicleRate', 'mean'),
    AvgSNAPRate       = ('SNAPRate', 'mean'),
    TotalSNAP         = ('TractSNAP', 'sum'),
    TotalNoVehicle    = ('TractHUNV', 'sum')
).reset_index()

state_stats['FoodDesertRate'] = (
    state_stats['FoodDesertTracts'] /
    state_stats['TotalTracts'] * 100
).round(2)

state_stats = state_stats.sort_values('FoodDesertRate', ascending=False)

print("\nTop 10 States by Food Desert Rate:")
print(state_stats[['State','FoodDesertTracts',
                    'FoodDesertRate','AvgPovertyRate',
                    'AvgIncome']].head(10).to_string(index=False))

# Save state stats
state_stats.to_csv("state_food_access_stats.csv", index=False)
print("✓ Saved state_food_access_stats.csv")

# ── 7. Urban vs Rural Breakdown ──────────────────────────────
print("\n── Urban vs Rural breakdown...")

urban_stats = df.groupby(['Urban', 'FoodDesert']).agg(
    Count      = ('CensusTract', 'count'),
    Population = ('Pop2010', 'sum')
).reset_index()

urban_stats['UrbanLabel']  = urban_stats['Urban'].map({1:'Urban', 0:'Rural'})
urban_stats['DesertLabel'] = urban_stats['FoodDesert'].map(
    {1:'Food Desert', 0:'Adequate Access'}
)

print(urban_stats[['UrbanLabel','DesertLabel',
                   'Count','Population']].to_string(index=False))

# ── 8. Export Clean Dataset ──────────────────────────────────
print("\n── Exporting clean dataset...")

cols = [
    'CensusTract', 'State', 'County', 'Urban', 'Pop2010',
    'FoodDesert', 'PovertyRate', 'MedianFamilyIncome',
    'NoVehicleRate', 'SNAPRate', 'PctBlack', 'PctHispanic',
    'PctSeniors', 'PctKids', 'TractHUNV', 'TractSNAP',
    'LowIncomeTracts', 'LILATracts_Vehicle', 'LILATracts_halfAnd10'
]

df_clean = df[cols].copy()
df_clean.to_csv("food_access_clean.csv", index=False)
print(f"✓ Exported {len(df_clean):,} rows to food_access_clean.csv")

# ── 9. Publish to ArcGIS Online ──────────────────────────────
print("\n── Publishing to ArcGIS Online...")

# Upload CSV
csv_item = gis.content.add({
    "title": "US Food Access Analysis 2019",
    "type":  "CSV",
    "tags":  "food desert, food access, USDA, census tract",
    "snippet": "USDA Food Access Research Atlas 2019 — cleaned for spatial analysis"
}, data="food_access_clean.csv")

print(f"✓ Uploaded CSV — Item ID: {csv_item.id}")

# Publish as hosted feature layer
published = csv_item.publish({
    "type":            "csv",
    "locationType":    "none",
    "columnDelimiter": ",",
    "qualifier":       '"',
    "name":            "US_Food_Access_Analysis_2019"
})

print(f"✓ Published feature layer: {published.title}")
print(f"  Item ID : {published.id}")
print(f"  URL     : {published.url}")
print(f"  View    : {published.homepage}")

print("\n✓ Pipeline complete.")
print("  Next: Open ArcGIS Online to style map, build dashboard,")
print("  and create Experience Builder app.")
