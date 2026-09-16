import geopandas as gpd
import folium
from pathlib import Path
import pandas as pd
import json

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output") / "maps"

print("="*80)
print("STAGE 3: BASIC INTERACTIVE MAPPING")
print("="*80)

# ============================================================================
# STEP 1: LOAD MERGED DATA
# ============================================================================

print("\n[STEP 1] Loading merged geospatial data...")

try:
    gdf = gpd.read_file(BASE_PATH / "processed" / "merged_data.geojson")
    print(f"✓ Loaded merged data: {len(gdf)} rows")
except FileNotFoundError:
    print("✗ Error: merged_data.geojson not found")
    print("  Make sure you ran Stage 2 first")
    exit()

# ============================================================================
# STEP 2: CLEAN DATA FOR MAPPING
# ============================================================================

print("\n[STEP 2] Cleaning data for JSON serialization...")

# Convert all Timestamp columns to strings
for col in gdf.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf[col]):
        gdf[col] = gdf[col].astype(str)

# Keep only essential columns for mapping
essential_cols = ['state_name', 'geopolitical_zone', 'pidgin_concentration_percent', 
                  'pidgin_speakers_estimate', 'financially_included_percent', 'geometry']
gdf = gdf[[col for col in essential_cols if col in gdf.columns]]

print(f"✓ Data cleaned and ready for mapping")

# ============================================================================
# STEP 3: DEFINE ZONE COLORS
# ============================================================================

print("\n[STEP 3] Setting up zone color scheme...")

zone_colors = {
    'North West': '#FF6B6B',      # Red
    'North Central': '#4ECDC4',   # Teal
    'North East': '#45B7D1',      # Blue
    'South West': '#FFA07A',      # Light salmon
    'South South': '#98D8C8',     # Mint
    'South East': '#F7DC6F'       # Yellow
}

print(f"✓ Color scheme ready for {len(zone_colors)} zones")

# ============================================================================
# STEP 4: CREATE BASE MAP CENTERED ON NIGERIA
# ============================================================================

print("\n[STEP 4] Creating base map...")

nigeria_center = [9.082, 8.675]

map_zones = folium.Map(
    location=nigeria_center,
    zoom_start=6,
    tiles='OpenStreetMap'
)

print(f"✓ Base map created, centered on {nigeria_center}")

# ============================================================================
# STEP 5: ADD GEOPOLITICAL ZONES AS LAYERS
# ============================================================================

print("\n[STEP 5] Adding geopolitical zones to map...")

# Group by geopolitical zone
for zone in sorted(gdf['geopolitical_zone'].dropna().unique()):
    zone_data = gdf[gdf['geopolitical_zone'] == zone]
    
    # Get color for this zone
    color = zone_colors.get(zone, '#888888')
    
    # Convert to GeoJSON
    geo_json = json.loads(zone_data.to_json())
    
    # Add to map
    folium.GeoJson(
        data=geo_json,
        style_function=lambda x, col=color: {
            'fillColor': col,
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.6
        },
        tooltip=zone,
        popup=zone
    ).add_to(map_zones)
    
    print(f"  ✓ Added {zone}: {len(zone_data)} states")

# ============================================================================
# STEP 6: ADD STATE LABELS AND POPUPS
# ============================================================================

print("\n[STEP 6] Adding state labels and information...")

label_count = 0
for idx, row in gdf.iterrows():
    try:
        # Get centroid of each state for label placement
        centroid = row.geometry.centroid
        
        # Create popup text
        popup_text = f"""
        <b>{row['state_name']}</b><br>
        Zone: {row['geopolitical_zone']}<br>
        Pidgin Concentration: {row['pidgin_concentration_percent']:.1f}%
        """
        
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=row['state_name'],
            icon=folium.Icon(icon='', prefix='', color='white', icon_color='black')
        ).add_to(map_zones)
        
        label_count += 1
    except Exception as e:
        print(f"  Warning: Could not add label for {row.get('state_name', 'Unknown')}: {e}")

print(f"✓ Added {label_count} state labels")

# ============================================================================
# STEP 7: ADD LEGEND
# ============================================================================

print("\n[STEP 7] Adding legend...")

legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 280px; height: auto; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 15px; border-radius: 5px;">
<h4 style="margin: 0 0 10px 0;">Nigeria Geopolitical Zones</h4>
<hr style="margin: 5px 0;">
'''

for zone in sorted(zone_colors.keys()):
    color = zone_colors[zone]
    legend_html += f'<p style="margin: 5px 0;"><span style="background-color: {color}; padding: 8px 12px; margin-right: 8px; border-radius: 3px;">■</span>{zone}</p>'

legend_html += '</div>'

map_zones.get_root().html.add_child(folium.Element(legend_html))

print("✓ Legend added to map")

# ============================================================================
# STEP 8: SAVE MAP
# ============================================================================

print("\n[STEP 8] Saving map...")

map_file = OUTPUT_PATH / "01_nigeria_zones_map.html"

try:
    map_zones.save(str(map_file))
    print(f"✓ Map saved successfully to {map_file}")
except Exception as e:
    print(f"✗ Error saving map: {e}")
    exit()

# ============================================================================
# STEP 9: SUMMARY STATISTICS
# ============================================================================

print("\n[STEP 9] Map Summary Statistics...")

print(f"\nStates per geopolitical zone:")
zone_counts = gdf[gdf['geopolitical_zone'].notna()]['geopolitical_zone'].value_counts().sort_index()
for zone, count in zone_counts.items():
    print(f"  {zone}: {count} states")

print(f"\nPidgin concentration summary:")
pidgin_stats = gdf[['geopolitical_zone', 'pidgin_concentration_percent']].groupby('geopolitical_zone').agg(['min', 'mean', 'max']).round(1)
print(pidgin_stats)

# ============================================================================
# FINAL STATUS
# ============================================================================

print("\n" + "="*80)
print("STAGE 3 COMPLETE - NO ERRORS")
print("="*80)
print(f"""
✓ Interactive map created successfully
✓ {len(gdf)} states mapped
✓ {len(zone_colors)} geopolitical zones color-coded
✓ {label_count} state labels with popup information added
✓ Legend included with all zones

MAP FILE CREATED:
  {map_file}

TO VIEW THE MAP:
  1. Open {map_file} in your web browser
  2. Click on state markers for information
  3. Hover over states for names

NEXT STEP (Stage 4):
  - Create choropleth map (states colored by Pidgin %)
  - Add financial inclusion data overlay
  - Create advanced visualization with multiple data layers
""")