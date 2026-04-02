# ============================================================
# California Food Desert Analysis — Complete Pipeline
# ============================================================

# ── 1. Install & Imports ─────────────────────────────────────
!pip install arcgis -q

from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
import numpy as np
import json
import requests
import time
import os
import warnings
warnings.filterwarnings("ignore")

print("✓ Libraries loaded")

# ── 2. Authenticate ──────────────────────────────────────────
UCI_URL   = "https://ucirvine.maps.arcgis.com"
CLIENT_ID = "XXX"

gis = GIS(UCI_URL, client_id=CLIENT_ID)
print(f"✓ Authenticated as: {gis.users.me.username}")


df = pd.read_excel(
    "/content/FoodAccessResearchAtlasData2019.xlsx",  # replace with your actual path
    sheet_name="Food Access Research Atlas"
)

print(f"✓ Loaded {len(df):,} rows")

# ── 4. Clean & Engineer Features ─────────────────────────────
df = df[df['Pop2010'] > 0].copy()

df['FoodDesert']         = df['LILATracts_1And10'].fillna(0).astype(int)
df['PovertyRate']        = df['PovertyRate'].fillna(0).round(2)
df['MedianFamilyIncome'] = df['MedianFamilyIncome'].fillna(0).round(0)
df['NoVehicleRate']      = (df['TractHUNV'] / df['Pop2010'] * 100).fillna(0).round(2)
df['SNAPRate']           = (df['TractSNAP'] / df['Pop2010'] * 100).fillna(0).round(2)
df['PctBlack']           = (df['TractBlack'] / df['Pop2010'] * 100).fillna(0).round(2)
df['PctHispanic']        = (df['TractHispanic'] / df['Pop2010'] * 100).fillna(0).round(2)
df['PctSeniors']         = (df['TractSeniors'] / df['Pop2010'] * 100).fillna(0).round(2)
df['PctKids']            = (df['TractKids'] / df['Pop2010'] * 100).fillna(0).round(2)
df['CensusTract']        = df['CensusTract'].astype(str).str.zfill(11)

# Filter to California only
ca_df = df[df['State'] == 'California'].copy()

print(f"✓ California tracts: {len(ca_df):,}")
print(f"✓ Food desert tracts: {ca_df['FoodDesert'].sum():,.0f}")
print(f"✓ Food desert rate: {ca_df['FoodDesert'].mean()*100:.1f}%")
print(f"✓ Population in food deserts: {ca_df[ca_df['FoodDesert']==1]['Pop2010'].sum():,}")

# ── 5. Download California Census Tract Boundaries ───────────
print("\nDownloading California census tract boundaries...")

url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/14/query"

all_features = []
offset = 0

while True:
    params = {
        "where": "STATE = '06'",  # California FIPS = 06
        "outFields": "GEOID",
        "outSR": "4326",
        "f": "geojson",
        "returnGeometry": "true",
        "resultRecordCount": 1000,
        "resultOffset": offset
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        features = data.get('features', [])
        
        if not features:
            break
            
        all_features.extend(features)
        print(f"  Downloaded {len(all_features):,} tracts...")
        
        if len(features) < 1000:
            break
            
        offset += 1000
        time.sleep(0.3)
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
        break

print(f"✓ Downloaded {len(all_features):,} California tract boundaries")

# ── 6. Merge Geometry with Food Access Data ──────────────────
print("\nMerging geometry with food access attributes...")

food_lookup = ca_df.set_index('CensusTract').to_dict('index')

essential_fields = [
    'State', 'County', 'FoodDesert', 'PovertyRate',
    'MedianFamilyIncome', 'NoVehicleRate', 'SNAPRate',
    'PctBlack', 'PctHispanic', 'PctSeniors', 'PctKids',
    'Pop2010', 'LowIncomeTracts'
]

merged_features = []
no_match = 0

for feature in all_features:
    geoid = feature['properties'].get('GEOID')
    if geoid in food_lookup:
        attrs = food_lookup[geoid]
        slim_props = {k: attrs.get(k) for k in essential_fields}
        slim_props['GEOID'] = geoid
        merged_features.append({
            "type": "Feature",
            "geometry": feature['geometry'],
            "properties": slim_props
        })
    else:
        no_match += 1

print(f"✓ Matched: {len(merged_features):,} features")
print(f"  No match: {no_match}")

# ── 7. Save GeoJSON ──────────────────────────────────────────
geojson_out = {
    "type": "FeatureCollection",
    "features": merged_features
}

with open("california_food_access.geojson", "w") as f:
    json.dump(geojson_out, f)

size = os.path.getsize("california_food_access.geojson") / 1024 / 1024
print(f"✓ Saved california_food_access.geojson — {size:.1f} MB")

# ── 8. Upload to ArcGIS Online ───────────────────────────────
print("\nUploading to ArcGIS Online...")

# Delete existing item if it exists
existing = gis.content.search(
    f"title:'California Food Access Analysis' owner:{gis.users.me.username}"
)
for item in existing:
    item.delete()
    print(f"  Deleted old item: {item.title}")

# Upload GeoJSON
geojson_item = gis.content.add({
    "title": "California Food Access Analysis",
    "type": "GeoJson",
    "tags": "food desert, California, USDA, GIS, poverty",
    "snippet": "USDA Food Access Research Atlas 2019 — California census tracts with food desert analysis"
}, data="california_food_access.geojson")

print(f"✓ Uploaded — Item ID: {geojson_item.id}")

# Publish as feature layer
published = geojson_item.publish()

print(f"✓ Published: {published.title}")
print(f"  Item ID : {published.id}")
print(f"  URL     : {published.url}")
print(f"  View    : {published.homepage}")

# Share publicly
published.share(everyone=True)
print(f"✓ Shared publicly")

# ── 9. Summary Stats ─────────────────────────────────────────
print("\n── California Food Desert Summary ──")
print(f"Total tracts analyzed : {len(ca_df):,}")
print(f"Food desert tracts    : {ca_df['FoodDesert'].sum():,.0f}")
print(f"Food desert rate      : {ca_df['FoodDesert'].mean()*100:.1f}%")
print(f"Pop in food deserts   : {ca_df[ca_df['FoodDesert']==1]['Pop2010'].sum():,}")

desert = ca_df[ca_df['FoodDesert']==1]
non    = ca_df[ca_df['FoodDesert']==0]

print(f"\nFood Desert Tracts vs Non:")
print(f"  Avg Poverty Rate    : {desert['PovertyRate'].mean():.1f}% vs {non['PovertyRate'].mean():.1f}%")
print(f"  Avg Income          : ${desert['MedianFamilyIncome'].mean():,.0f} vs ${non['MedianFamilyIncome'].mean():,.0f}")
print(f"  Avg No Vehicle Rate : {desert['NoVehicleRate'].mean():.1f}% vs {non['NoVehicleRate'].mean():.1f}%")
print(f"  Avg SNAP Rate       : {desert['SNAPRate'].mean():.1f}% vs {non['SNAPRate'].mean():.1f}%")
print(f"  Avg % Hispanic      : {desert['PctHispanic'].mean():.1f}% vs {non['PctHispanic'].mean():.1f}%")

print("\n✓ Pipeline complete — open ArcGIS Online to build map, dashboard, and Experience Builder")
