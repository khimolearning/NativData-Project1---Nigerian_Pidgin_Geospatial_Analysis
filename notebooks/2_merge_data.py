import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE_PATH = Path("data")

print("="*80)
print("STAGE 2: DATA MERGING & PREPARATION")
print("="*80)

# ============================================================================
# STEP 1: LOAD ALL DATA
# ============================================================================

print("\n[STEP 1] Loading all data sources...")

# Load the three CSVs
df_geo = pd.read_csv(BASE_PATH / "raw" / "1_gp_zones.csv")
df_pidgin = pd.read_csv(BASE_PATH / "raw" / "2_pidgin_state.csv")
df_efinadata = pd.read_csv(BASE_PATH / "raw" / "3_efindata_2023.csv")

# Load shapefile
gdf_nigeria = gpd.read_file(BASE_PATH / "shapefiles" / "nga_admin1.shp")

print(f"✓ Loaded geopolitical zones: {len(df_geo)} rows")
print(f"✓ Loaded pidgin data: {len(df_pidgin)} rows")
print(f"✓ Loaded EFInA data: {len(df_efinadata)} rows")
print(f"✓ Loaded Nigeria shapefile: {len(gdf_nigeria)} rows")

# ============================================================================
# STEP 2: INSPECT COLUMN NAMES (Find the matching keys)
# ============================================================================

print("\n[STEP 2] Checking column names for merging...")
print(f"\nShapefile columns: {list(gdf_nigeria.columns)}")
print(f"Pidgin data columns: {list(df_pidgin.columns)}")
print(f"EFInA data columns: {list(df_efinadata.columns)}")

# The state name column in shapefile is 'adm1_name'
print(f"\nShapefile first 5 state names:")
print(gdf_nigeria[['adm1_name', 'adm1_pcode']].head())

# ============================================================================
# STEP 3: PREPARE DATA - STANDARDIZE STATE NAMES
# ============================================================================

print("\n[STEP 3] Standardizing state names for matching...")

print(f"\nShapefile state names (all 37):")
print(gdf_nigeria['adm1_name'].unique())

print(f"\nPidgin data state names (all 37):")
print(df_pidgin['state_name'].unique())

# ============================================================================
# STEP 4: MERGE SHAPEFILE + PIDGIN DATA
# ============================================================================

print("\n[STEP 4] Merging shapefile with pidgin speaker data...")

# Rename shapefile column 'adm1_name' to 'state_name' to match pidgin data
gdf_merged = gdf_nigeria.copy()
gdf_merged['state_name'] = gdf_nigeria['adm1_name']

# Left join: Keep all states in shapefile, add pidgin data where it matches
gdf_merged = gdf_merged.merge(
    df_pidgin,
    on='state_name',
    how='left'
)

print(f"✓ Merged shapefile + pidgin data: {len(gdf_merged)} rows")

missing_pidgin = gdf_merged[gdf_merged['pidgin_concentration_percent'].isna()]
if len(missing_pidgin) > 0:
    print(f"\nRows with missing pidgin data:")
    print(missing_pidgin[['state_name', 'pidgin_concentration_percent']])
else:
    print(f"✓ All states have pidgin data")

# ============================================================================
# STEP 5: MERGE WITH EFINADATA (by geopolitical zone)
# ============================================================================

print("\n[STEP 5] Merging with EFInA financial inclusion data...")

# Now merge with EFInA data using geopolitical_zone as key
gdf_merged = gdf_merged.merge(
    df_efinadata,
    on='geopolitical_zone',
    how='left'
)

print(f"✓ Final merged dataset: {len(gdf_merged)} rows")

# ============================================================================
# STEP 6: DATA QUALITY CHECK
# ============================================================================

print("\n[STEP 6] Data quality check...")

print(f"\nMissing values in key columns:")
key_columns = ['state_name', 'pidgin_concentration_percent', 'financially_included_percent']
for col in key_columns:
    missing_count = gdf_merged[col].isnull().sum()
    print(f" {col}: {missing_count} missing")

print(f"\nSample of merged data (10 states):")
display_cols = [
    'state_name', 
    'geopolitical_zone',
    'pidgin_concentration_percent',
    'pidgin_speakers_estimate',
    'financially_included_percent'
]
print(gdf_merged[display_cols].head(10).to_string())

# ============================================================================
# STEP 7: SAVE MERGED DATA
# ============================================================================

print("\n[STEP 7] Saving merged dataset...")

# Save as GeoJSON (keeps geometry + all data)
output_path = BASE_PATH / "processed" / "merged_data.geojson"
gdf_merged.to_file(output_path, driver='GeoJSON')
print(f"✓ Saved GeoJSON to {output_path}")

# Also save as CSV for reference (without geometry)
csv_output = BASE_PATH / "processed" / "merged_data.csv"
gdf_merged.drop(columns=['geometry']).to_csv(csv_output, index=False)
print(f"✓ Saved CSV to {csv_output}")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n[STEP 8] Summary Statistics...")

print(f"\nPidgin concentration by geopolitical zone:")
zone_summary = gdf_merged.groupby('geopolitical_zone').agg({
    'pidgin_concentration_percent': 'mean',
    'financially_included_percent': 'mean',
    'pidgin_speakers_estimate': 'sum'
}).round(2)
print(zone_summary)

print(f"\nTop 5 states by Pidgin concentration:")
top_pidgin = gdf_merged.nlargest(5, 'pidgin_concentration_percent')[
    ['state_name', 'pidgin_concentration_percent', 'geopolitical_zone']
]
print(top_pidgin.to_string())

print(f"\nTop 5 zones by Financial inclusion:")
top_finance = gdf_merged.drop_duplicates('geopolitical_zone').nlargest(5, 'financially_included_percent')[
    ['geopolitical_zone', 'financially_included_percent']
]
print(top_finance.to_string())

# ============================================================================
# FINAL STATUS
# ============================================================================

print("\n" + "="*80)
print("STAGE 2 COMPLETE")
print("="*80)
print(f"""
✓ All data merged successfully
✓ {len(gdf_merged)} states/regions ready for mapping
✓ Pidgin concentration data: {gdf_merged['pidgin_concentration_percent'].notna().sum()}/37 states
✓ Financial inclusion data: {gdf_merged['financially_included_percent'].notna().sum()}/37 rows

OUTPUT FILES CREATED:
  1. {output_path}
  2. {csv_output}

NEXT STEP (Stage 3):
- Create interactive map showing Nigeria's 6 geopolitical zones
- Color code states by Pidgin concentration
- Add labels and hover information
""")
