import geopandas as gpd
import folium
from folium import plugins
from pathlib import Path
import pandas as pd
import json

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output") / "maps"

print("="*80)
print("STAGE 4: PIDGIN CONCENTRATION CHOROPLETH MAP")
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
# STEP 2: DATA QUALITY CHECK
# ============================================================================

print("\n[STEP 2] Checking data quality...")

# Convert timestamp columns to strings
for col in gdf.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf[col]):
        gdf[col] = gdf[col].astype(str)

# Check for pidgin data
pidgin_data_count = gdf['pidgin_concentration_percent'].notna().sum()
print(f"✓ Pidgin concentration data available for {pidgin_data_count} states")

# Get data range
min_pidgin = gdf['pidgin_concentration_percent'].min()
max_pidgin = gdf['pidgin_concentration_percent'].max()
print(f"✓ Data range: {min_pidgin}% to {max_pidgin}%")

# ============================================================================
# STEP 3: CREATE COLOR SCALE (COLORMAP)
# ============================================================================

print("\n[STEP 3] Creating color scale...")

# We'll use a red-to-yellow color scheme
# Red = low Pidgin (North), Yellow = high Pidgin (South)
min_val = gdf['pidgin_concentration_percent'].min()
max_val = gdf['pidgin_concentration_percent'].max()

def get_color(pidgin_percent):
    """
    Returns a color based on Pidgin concentration percentage.
    Red (low) to Yellow (high)
    """
    if pd.isna(pidgin_percent):
        return '#808080'  # Gray for missing data
    
    # Normalize value between 0 and 1
    normalized = (pidgin_percent - min_val) / (max_val - min_val)
    
    # Red to Yellow gradient
    # Red = (255, 0, 0)
    # Yellow = (255, 255, 0)
    if normalized < 0.25:
        # Dark red to red
        r = 255
        g = int(0 + (normalized / 0.25) * 50)
        b = 0
    elif normalized < 0.5:
        # Red to orange
        r = 255
        g = int(50 + ((normalized - 0.25) / 0.25) * 100)
        b = 0
    elif normalized < 0.75:
        # Orange to light orange
        r = 255
        g = int(150 + ((normalized - 0.5) / 0.25) * 105)
        b = 0
    else:
        # Light orange to yellow
        r = 255
        g = int(255)
        b = 0
    
    return f'#{r:02x}{g:02x}{b:02x}'

print("✓ Color scale ready (red=low, yellow=high)")

# ============================================================================
# STEP 4: CREATE BASE MAP
# ============================================================================

print("\n[STEP 4] Creating base map...")

nigeria_center = [9.082, 8.675]

map_choropleth = folium.Map(
    location=nigeria_center,
    zoom_start=6,
    tiles='OpenStreetMap'
)

print("✓ Base map created")

# ============================================================================
# STEP 5: ADD CHOROPLETH LAYER
# ============================================================================

print("\n[STEP 5] Adding choropleth layer...")

# Convert to GeoJSON
geo_json = json.loads(gdf.to_json())

# Add choropleth
for feature in geo_json['features']:
    properties = feature['properties']
    state_name = properties.get('state_name', 'Unknown')
    pidgin_percent = properties.get('pidgin_concentration_percent')
    
    # Handle missing data
    if pidgin_percent is None:
        pidgin_percent = 0
    
    color = get_color(pidgin_percent)
    
    folium.GeoJson(
        data=feature,
        style_function=lambda x, c=color: {
            'fillColor': c,
            'color': 'black',
            'weight': 1.5,
            'fillOpacity': 0.8
        },
        tooltip=state_name,
        popup=folium.Popup(
            f"<b>{state_name}</b><br>Pidgin: {pidgin_percent:.1f}%",
            max_width=250
        )
    ).add_to(map_choropleth)

print("✓ Choropleth layer added")

# ============================================================================
# STEP 6: ADD STATE LABELS
# ============================================================================

print("\n[STEP 6] Adding state labels...")

label_count = 0
for idx, row in gdf.iterrows():
    try:
        centroid = row.geometry.centroid
        
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=folium.Popup(
                f"<b>{row['state_name']}</b><br>"
                f"Pidgin: {row['pidgin_concentration_percent']:.1f}%<br>"
                f"Speakers: {row['pidgin_speakers_estimate']:,.0f}",
                max_width=250
            ),
            tooltip=row['state_name'],
            icon=folium.Icon(icon='', prefix='', color='white', 
                           icon_color='black')
        ).add_to(map_choropleth)
        
        label_count += 1
    except Exception as e:
        pass

print(f"✓ Added {label_count} state labels")

# ============================================================================
# STEP 7: ADD INTERACTIVE LEGEND
# ============================================================================

print("\n[STEP 7] Adding interactive legend...")

legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 320px; height: auto; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:13px; padding: 15px; border-radius: 5px;
            font-family: Arial, sans-serif;">
            
<h3 style="margin: 0 0 10px 0; font-size: 15px;">
Pidgin Speaker Concentration
</h3>
<hr style="margin: 5px 0;">

<div style="display: flex; align-items: center; margin: 8px 0;">
  <div style="background-color: #ff0000; width: 30px; height: 20px; 
              border: 1px solid black; margin-right: 10px;"></div>
  <span>Low ({min_pidgin:.1f}%)</span>
</div>

<div style="display: flex; align-items: center; margin: 8px 0;">
  <div style="background-color: #ffaa00; width: 30px; height: 20px; 
              border: 1px solid black; margin-right: 10px;"></div>
  <span>Medium ({(min_pidgin + max_pidgin)/2:.1f}%)</span>
</div>

<div style="display: flex; align-items: center; margin: 8px 0;">
  <div style="background-color: #ffff00; width: 30px; height: 20px; 
              border: 1px solid black; margin-right: 10px;"></div>
  <span>High ({max_pidgin:.1f}%)</span>
</div>

<hr style="margin: 10px 0;">
<p style="font-size: 12px; margin: 5px 0; font-style: italic;">
Click states for details | Darker = More speakers
</p>
</div>
'''

map_choropleth.get_root().html.add_child(folium.Element(legend_html))

print("✓ Legend added")

# ============================================================================
# STEP 8: ADD STATISTICS INFO BOX
# ============================================================================

print("\n[STEP 8] Adding statistics info box...")

stats_html = f'''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 300px; height: auto; 
            background-color: #f9f9f9; border:2px solid #333; z-index:9999; 
            font-size:12px; padding: 15px; border-radius: 5px;
            font-family: Arial, sans-serif;">
            
<h4 style="margin: 0 0 10px 0; font-size: 14px;">Pidgin Statistics</h4>
<hr style="margin: 5px 0;">

<p style="margin: 5px 0;">
<b>Highest:</b> {gdf.loc[gdf['pidgin_concentration_percent'].idxmax(), 'state_name']} 
({gdf['pidgin_concentration_percent'].max():.1f}%)
</p>

<p style="margin: 5px 0;">
<b>Lowest:</b> {gdf.loc[gdf['pidgin_concentration_percent'].idxmin(), 'state_name']} 
({gdf['pidgin_concentration_percent'].min():.1f}%)
</p>

<p style="margin: 5px 0;">
<b>Average:</b> {gdf['pidgin_concentration_percent'].mean():.1f}%
</p>

<p style="margin: 5px 0;">
<b>Total Speakers:</b> {gdf['pidgin_speakers_estimate'].sum():,.0f}
</p>
</div>
'''

map_choropleth.get_root().html.add_child(folium.Element(stats_html))

print("✓ Statistics box added")

# ============================================================================
# STEP 9: SAVE MAP
# ============================================================================

print("\n[STEP 9] Saving map...")

map_file = OUTPUT_PATH / "02_pidgin_concentration_map.html"

try:
    map_choropleth.save(str(map_file))
    print(f"✓ Map saved to {map_file}")
except Exception as e:
    print(f"✗ Error saving map: {e}")
    exit()

# ============================================================================
# STEP 10: SUMMARY
# ============================================================================

print("\n[STEP 10] Summary...")

zone_summary = gdf.groupby('geopolitical_zone').agg({
    'pidgin_concentration_percent': ['mean', 'min', 'max'],
    'state_name': 'count'
}).round(1)

print("\nPidgin Concentration by Geopolitical Zone:")
print(zone_summary)

print("\nTop 5 States by Pidgin Concentration:")
top_states = gdf.nlargest(5, 'pidgin_concentration_percent')[
    ['state_name', 'pidgin_concentration_percent', 'geopolitical_zone']
]
for idx, row in top_states.iterrows():
    print(f"  {row['state_name']:20s} {row['pidgin_concentration_percent']:5.1f}% ({row['geopolitical_zone']})")

# ============================================================================
# FINAL MESSAGE
# ============================================================================

print("\n" + "="*80)
print("STAGE 4 COMPLETE - CHOROPLETH MAP READY")
print("="*80)
print(f"""
✓ Choropleth map created successfully
✓ {len(gdf)} states colored by Pidgin concentration
✓ Color gradient: Red (low) to Yellow (high)
✓ Interactive popups with statistics
✓ Legend and statistics box added

MAP FILE:
  {map_file}

TO VIEW:
  Open {map_file} in your web browser

WHAT THE MAP SHOWS:
  - South: Darker colors (high Pidgin concentration)
  - North: Lighter colors (low Pidgin concentration)
  - Click states for exact percentages
  - Hover for state names

NEXT STEP (Stage 5):
  - Overlay EFInA financial inclusion data
  - Create correlation visualization
  - Add multi-layer interactivity
""")
