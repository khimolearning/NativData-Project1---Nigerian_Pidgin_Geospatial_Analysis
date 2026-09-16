#================================================================================
#COMPLETE CODE FOR 5_final_overlay_map.py
#================================================================================

import geopandas as gpd
import folium
from folium import plugins
from pathlib import Path
import pandas as pd
import json
import numpy as np

BASE_PATH = Path("data")
OUTPUT_PATH = Path("output") / "maps"

print("="*80)
print("STAGE 5: FINAL OVERLAY MAP - PIDGIN + FINANCIAL INCLUSION")
print("="*80)

# ============================================================================
# STEP 1: LOAD MERGED DATA
# ============================================================================

print("\n[STEP 1] Loading merged data...")

try:
    gdf = gpd.read_file(BASE_PATH / "processed" / "merged_data.geojson")
    print(f"✓ Loaded data: {len(gdf)} rows")
except FileNotFoundError:
    print("✗ Error: merged_data.geojson not found")
    exit()

# Convert timestamps to strings
for col in gdf.columns:
    if pd.api.types.is_datetime64_any_dtype(gdf[col]):
        gdf[col] = gdf[col].astype(str)

# ============================================================================
# STEP 2: PREPARE DATA FOR DUAL VISUALIZATION
# ============================================================================

print("\n[STEP 2] Preparing data for dual visualization...")

pidgin_min = gdf['pidgin_concentration_percent'].min()
pidgin_max = gdf['pidgin_concentration_percent'].max()
finance_min = gdf['financially_included_percent'].min()
finance_max = gdf['financially_included_percent'].max()

print(f"✓ Pidgin range: {pidgin_min}% to {pidgin_max}%")
print(f"✓ Finance range: {finance_min}% to {finance_max}%")

# Calculate correlation
pidgin_series = gdf['pidgin_concentration_percent'].dropna()
finance_series = gdf['financially_included_percent'].dropna()
correlation = pidgin_series.corr(finance_series)
print(f"✓ Correlation: {correlation:.3f}")

# ============================================================================
# STEP 3: CREATE BASE MAP
# ============================================================================

print("\n[STEP 3] Creating base map...")

nigeria_center = [9.082, 8.675]

map_final = folium.Map(
    location=nigeria_center,
    zoom_start=6,
    tiles='OpenStreetMap'
)

print("✓ Base map created")

# ============================================================================
# STEP 4: ADD PIDGIN CHOROPLETH LAYER
# ============================================================================

print("\n[STEP 4] Adding Pidgin choropleth layer...")

def get_pidgin_color(pidgin_percent):
    """Red (low) to Yellow (high) color scale"""
    if pd.isna(pidgin_percent):
        return '#808080'
    
    normalized = (pidgin_percent - pidgin_min) / (pidgin_max - pidgin_min)
    
    if normalized < 0.25:
        r = 255
        g = int(0 + (normalized / 0.25) * 50)
        b = 0
    elif normalized < 0.5:
        r = 255
        g = int(50 + ((normalized - 0.25) / 0.25) * 100)
        b = 0
    elif normalized < 0.75:
        r = 255
        g = int(150 + ((normalized - 0.5) / 0.25) * 105)
        b = 0
    else:
        r = 255
        g = int(255)
        b = 0
    
    return f'#{r:02x}{g:02x}{b:02x}'

geo_json = json.loads(gdf.to_json())

for feature in geo_json['features']:
    properties = feature['properties']
    state_name = properties.get('state_name', 'Unknown')
    pidgin_percent = properties.get('pidgin_concentration_percent')
    finance_percent = properties.get('financially_included_percent')
    
    if pidgin_percent is None:
        pidgin_percent = 0
    if finance_percent is None:
        finance_percent = 0
    
    color = get_pidgin_color(pidgin_percent)
    
    folium.GeoJson(
        data=feature,
        style_function=lambda x, c=color: {
            'fillColor': c,
            'color': 'black',
            'weight': 1.5,
            'fillOpacity': 0.7
        },
        tooltip=state_name,
        popup=folium.Popup(
            f"<b>{state_name}</b><br>"
            f"Pidgin: {pidgin_percent:.1f}%<br>"
            f"Financial Inclusion: {finance_percent:.1f}%",
            max_width=250
        )
    ).add_to(map_final)

print("✓ Choropleth complete")

# ============================================================================
# STEP 5: ADD FINANCIAL INCLUSION CIRCLE MARKERS (by zone)
# ============================================================================

print("\n[STEP 5] Adding financial inclusion circle markers...")

zone_colors_circle = {
    'North West': '#FF6B6B',
    'North Central': '#4ECDC4',
    'North East': '#45B7D1',
    'South West': '#FFA07A',
    'South South': '#98D8C8',
    'South East': '#F7DC6F'
}

# Calculate zone centroids and finance values
zone_summary = gdf.groupby('geopolitical_zone').agg({
    'financially_included_percent': 'mean'
}).reset_index()

# Add centroids separately
for idx, row in zone_summary.iterrows():
    zone_name = row['geopolitical_zone']
    finance_pct = row['financially_included_percent']
    
    # Get all states in this zone and calculate centroid
    zone_states = gdf[gdf['geopolitical_zone'] == zone_name]
    zone_geometry = zone_states.unary_union
    centroid = zone_geometry.centroid
    
    # Size circles by finance percentage (scale 10-50)
    circle_radius = 10 + (finance_pct / finance_max) * 40
    
    folium.CircleMarker(
        location=[centroid.y, centroid.x],
        radius=circle_radius,
        popup=folium.Popup(
            f"<b>{zone_name}</b><br>"
            f"Avg Financial Inclusion: {finance_pct:.1f}%<br>"
            f"Circle size shows finance %",
            max_width=250
        ),
        tooltip=f"{zone_name}: {finance_pct:.1f}%",
        color='black',
        fill=True,
        fillColor=zone_colors_circle.get(zone_name, '#888888'),
        fillOpacity=0.6,
        weight=2
    ).add_to(map_final)

print(f"✓ Added {len(zone_summary)} zone markers")

# ============================================================================
# STEP 6: ADD DUAL LEGEND
# ============================================================================

print("\n[STEP 6] Adding dual legend...")

legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 340px; height: auto; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:12px; padding: 15px; border-radius: 5px;
            font-family: Arial, sans-serif;">

<h3 style="margin: 0 0 10px 0; font-size: 14px;">Map Legend</h3>
<hr style="margin: 5px 0;">

<b>LAYER 1: States (Choropleth)</b>
<p style="margin: 5px 0; font-size: 11px;">Colored by Pidgin Concentration</p>
<div style="display: flex; align-items: center; margin: 5px 0;">
  <div style="background-color: #ff0000; width: 25px; height: 15px; 
              border: 1px solid black; margin-right: 8px;"></div>
  <span>Low ({pidgin_min:.0f}%)</span>
</div>
<div style="display: flex; align-items: center; margin: 5px 0;">
  <div style="background-color: #ffff00; width: 25px; height: 15px; 
              border: 1px solid black; margin-right: 8px;"></div>
  <span>High ({pidgin_max:.0f}%)</span>
</div>

<hr style="margin: 10px 0;">

<b>LAYER 2: Circles (Zones)</b>
<p style="margin: 5px 0; font-size: 11px;">Size = Financial Inclusion %</p>
<p style="margin: 5px 0; font-size: 10px;">
Larger circle = Better financial inclusion
</p>

<hr style="margin: 10px 0;">

<p style="margin: 5px 0; font-size: 11px; font-style: italic;">
Click states for details | Hover for tooltips
</p>
</div>
'''

map_final.get_root().html.add_child(folium.Element(legend_html))

print("✓ Legend added")

# ============================================================================
# STEP 7: ADD STATISTICS AND INSIGHTS BOX
# ============================================================================

print("\n[STEP 7] Adding statistics and insights...")

top_pidgin_state = gdf.loc[gdf['pidgin_concentration_percent'].idxmax()]
top_finance_zone = gdf.drop_duplicates('geopolitical_zone').loc[
    gdf.drop_duplicates('geopolitical_zone')['financially_included_percent'].idxmax()
]

stats_html = f'''
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 340px; height: auto; 
            background-color: #f0f8ff; border:2px solid #333; z-index:9999; 
            font-size:12px; padding: 15px; border-radius: 5px;
            font-family: Arial, sans-serif;">

<h4 style="margin: 0 0 10px 0; font-size: 13px;">Project Insights</h4>
<hr style="margin: 5px 0;">

<p style="margin: 5px 0;"><b>Pidgin Concentration:</b></p>
<p style="margin: 5px 0; font-size: 11px;">
Highest: {top_pidgin_state['state_name']} ({top_pidgin_state['pidgin_concentration_percent']:.1f}%)
</p>

<p style="margin: 5px 0;"><b>Financial Inclusion:</b></p>
<p style="margin: 5px 0; font-size: 11px;">
Best: {top_finance_zone['geopolitical_zone']} ({top_finance_zone['financially_included_percent']:.1f}%)
</p>

<p style="margin: 5px 0;"><b>Correlation:</b></p>
<p style="margin: 5px 0; font-size: 11px; font-weight: bold;">
{correlation:.3f}
</p>

<p style="margin: 5px 0; font-size: 10px; font-style: italic;">
{('Positive: Pidgin speakers in areas with better financial access' if correlation > 0 else 'Negative: Pidgin speakers in areas with lower financial access')}
</p>
</div>
'''

map_final.get_root().html.add_child(folium.Element(stats_html))

print("✓ Statistics box added")

# ============================================================================
# STEP 8: ADD CORRELATION ANALYSIS
# ============================================================================

print("\n[STEP 8] Adding correlation analysis...")

# Already calculated above
correlation_text = (
    f"Strong positive correlation ({correlation:.2f})" if correlation > 0.5 else
    f"Weak positive correlation ({correlation:.2f})" if correlation > 0 else
    f"Weak negative correlation ({correlation:.2f})" if correlation > -0.5 else
    f"Strong negative correlation ({correlation:.2f})"
)

print(f"✓ Correlation: {correlation_text}")

# ============================================================================
# STEP 9: SAVE FINAL MAP
# ============================================================================

print("\n[STEP 9] Saving final map...")

map_file = OUTPUT_PATH / "03_final_pidgin_finance_map.html"

try:
    map_final.save(str(map_file))
    print(f"✓ Map saved to {map_file}")
except Exception as e:
    print(f"✗ Error saving map: {e}")
    exit()

# ============================================================================
# STEP 10: SUMMARY
# ============================================================================

print("\n[STEP 10] Summary...")

print("\nZone Analysis:")
zone_analysis = gdf.drop_duplicates('geopolitical_zone')[
    ['geopolitical_zone', 'pidgin_concentration_percent', 'financially_included_percent']
].sort_values('pidgin_concentration_percent', ascending=False)

for idx, row in zone_analysis.iterrows():
    zone_name = str(row['geopolitical_zone'])  # Convert to string
    pidgin_pct = row['pidgin_concentration_percent']
    finance_pct = row['financially_included_percent']
    
    # Skip NaN zones
    if pd.isna(zone_name) or zone_name == 'nan':
        continue
    
    print(f"  {zone_name:20s} Pidgin: {pidgin_pct:5.1f}% | Finance: {finance_pct:5.1f}%")

# ============================================================================
# FINAL MESSAGE
# ============================================================================

print("\n" + "="*80)
print("STAGE 5 COMPLETE - FINAL OVERLAY MAP READY")
print("="*80)
print(f"""
✓ Final overlay map created successfully
✓ Dual-layer visualization complete
✓ Pidgin concentration (choropleth) + Financial inclusion (circles)
✓ Correlation calculated: {correlation:.3f}
✓ Interactive legends and statistics added

MAP FILE:
  {map_file}

KEY FINDING:
  {correlation_text}

INTERPRETATION:
  Correlation coefficient of {correlation:.3f} indicates a 
  {'strong positive' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.4 else 'weak'} 
  {'positive' if correlation > 0 else 'negative'} relationship between Pidgin 
  speaker concentration and financial inclusion.

NEXT STEP (Stage 6):
  - Create project documentation (README)
  - Write analysis summary
  - Create final portfolio report
  - Prepare for sharing/submission
""")
