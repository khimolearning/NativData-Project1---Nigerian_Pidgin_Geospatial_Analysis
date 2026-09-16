# NativData GIS Layer: Mapping Pidgin Speakers & Financial Inclusion Across Nigeria

## What This Project Does

This project visualizes the geographic spread of Nigerian Pidgin English speakers across Nigeria's six geopolitical zones and connects this language pattern to financial inclusion data. The result is an interactive map showing where Pidgin speakers live and how their regions compare in terms of banking access.

The key question: Where do Pidgin speakers live in Nigeria, and does this correlate with better financial inclusion?

The answer: Yes, strongly. Regions with more Pidgin speakers have significantly better financial access. The correlation is 0.839, which is about as strong as geographic correlations get.

## What You'll Find Here

Three interactive maps showing the same data at different levels:

1. **Nigeria Geopolitical Zones Map** - Basic map showing all 6 zones and state boundaries. This is your geographic reference.

2. **Pidgin Concentration Choropleth** - States colored from red (few Pidgin speakers) to yellow (many Pidgin speakers). This is where you see the south-north divide clearly.

3. **Final Overlay Map** - The main visualization. Shows Pidgin concentration as background colors PLUS circle markers representing financial inclusion by zone. This is the story of the entire project.

## The Main Finding

Pidgin speakers in Nigeria live in a clear south-to-north gradient. The south has extremely high Pidgin concentration (up to 90% in Rivers State). The north has much lower concentration (as low as 28% in Sokoto State). 

Financial inclusion follows a similar but not identical pattern. Southern regions with high Pidgin concentration also tend to have better access to banks and financial services.

The correlation is 0.839. This is statistically strong. It means that if you know the Pidgin concentration in a region, you can predict financial inclusion with decent accuracy.

## Why This Matters

Understanding where Pidgin speakers live helps us understand where economic activity and urbanization are strongest in Nigeria. Pidgin developed as a trade language in port cities. It spread along major commerce routes. Today, Pidgin concentration tells us something about regional development patterns.

Financial inclusion is critical for development. If Pidgin-speaking regions have better access to banking, policymakers should understand why. Is it because those regions are more urbanized? Because they have better infrastructure? Because they have more economic activity? All of these are related.

This project shows the geography of development in Nigeria. The maps let you see it visually.

## The Data Behind It

We combined data from three sources:

1. Nigeria state boundaries (from Humanitarian Data Exchange)
2. Estimates of Pidgin speaker concentration by state
3. EFInA financial inclusion data by geopolitical zone

We merged all this into one dataset and created three maps showing different views of the same story.

## How to View the Maps

All three maps are in the `output/maps/` folder:

- `01_nigeria_zones_map.html` - Click this to see zones
- `02_pidgin_concentration_map.html` - Click this to see Pidgin distribution
- `03_final_pidgin_finance_map.html` - Click this for the complete story

Just double-click any HTML file and it opens in your browser. The maps are interactive. Click on states to see numbers. Hover for tooltips. Zoom and pan to explore.

## How We Built It

The project uses Python with geospatial libraries:

- GeoPandas for handling geographic boundaries
- Folium for creating interactive web maps
- Pandas for data cleaning and merging
- Jupyter notebooks for analysis

The code is organized into 5 stages, each building on the previous:

Stage 1: Load and verify all data sources
Stage 2: Merge the three datasets into one
Stage 3: Create a basic map showing zones
Stage 4: Color states by Pidgin concentration
Stage 5: Add financial inclusion data on top

Each stage is a separate Python script that you can run independently.

## Key Insights From the Data

**Insight 1: The South-North Divide**

Pidgin concentration drops dramatically as you move north. The South West, South South, and South East zones average 70+ percent Pidgin concentration. The North West and North East zones average 30-40 percent. This is not gradual. It's a sharp divide.

**Insight 2: Financial Inclusion Follows but Isn't Identical**

The same zones with high Pidgin also have high financial inclusion. But the correlation isn't perfect. Some northern zones have better financial inclusion than expected given their Pidgin levels. This tells us that banking access depends on more than just Pidgin presence. Infrastructure, policy, education all matter.

**Insight 3: Lagos Drives Everything**

Lagos is an outlier. It has 85 percent Pidgin concentration and 65 percent financial inclusion. Lagos is Nigeria's economic engine. It pulls the national averages up.

**Insight 4: North Central is Surprisingly Inclusive**

The North Central zone has moderate Pidgin concentration (48%) but relatively high financial inclusion for the north (48%). This is probably because Abuja, the capital, is in this zone. Government employment and infrastructure concentrate banking access there.

**Insight 5: The Informal Economy Matters**

Some regions with high Pidgin speakers have lower formal financial inclusion. This might mean they have strong informal economies. Mobile money and informal savings groups might be more important than formal banks in some areas.

## What This Means For Development

If you're a policymaker trying to improve financial inclusion in Nigeria:

1. Don't assume Pidgin-speaking regions need more help. They're already more financially inclusive.

2. Focus on the north. Pidgin concentration is low, but financial inclusion is also low. This suggests deeper infrastructure and economic challenges.

3. Understand that language patterns reflect underlying development patterns. Pidgin concentration is a symptom of urbanization and commerce, not a cause of financial inclusion. Fix the underlying factors and both will improve.

4. Consider informal finance. Some regions with high Pidgin speakers use mobile money and informal groups more than formal banks. This isn't financial exclusion if people have access. It's just different financial systems.

## For Researchers and Data Scientists

The methodology here is straightforward but useful:

1. We took geographic boundaries (shapefiles) and merged them with statistical data (CSVs)
2. We created visualizations at different levels of detail
3. We calculated correlation to test relationships
4. We overlaid multiple data sources on one map

This approach works for many geographic analyses. If you want to study health, education, agriculture, or anything else at the geographic level, this is the framework.

The code is on GitHub. You can fork it, modify it, and use it for your own projects.

## Learning Resources

If you want to learn more about geospatial analysis in Python:

- GeoPandas documentation: geopandas.org
- Folium documentation: python-visualization.github.io/folium
- "Geospatial Analysis with Python" courses are available on Coursera and Udemy

The skills here translate to many fields. Urban planning uses these tools. Environmental science uses them. Public health uses them. Development economics uses them.

## About the Project

This is a portfolio project created to demonstrate geospatial data analysis skills. It was built completely from raw data. No tutorials were used. No datasets were pre-processed.

The project includes:
- Data sourcing
- Data cleaning and merging
- Exploratory analysis
- Visualization design
- Statistical analysis
- Documentation

All code is available on GitHub for review and reproducibility.

## Next Steps

This is Project 1 of a data science portfolio. Project 2 will apply the same geospatial analysis methods to health data: mapping cancer and type 2 diabetes across Nigeria.

Later projects will add machine learning, time series analysis, and more advanced statistical methods.

The goal is to build a strong portfolio showing real skills with real data and real insights.

## Questions?

The complete analysis is in ANALYSIS_SUMMARY.txt. It explains the methodology, the findings, and the limitations in detail.

The code is available to review if you want to understand how something was done.

The maps are interactive if you want to explore the data yourself.
