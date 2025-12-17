# Load Libraries
# NOTE: If you are running this locally, ensure you have these libraries installed:
# pip install pandas geopandas matplotlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. DATA LOADING AND INITIAL PREPARATION

#IMPORTANT: UPDATE THESE PATHS TO YOUR LOCAL FILES 
# Use your exact local file paths here for kt_df and pop_df
kt_df = pd.read_csv('E:/Python/ProjectDS150/kwiktrip.csv')
pop_df = pd.read_csv('E:/Python/ProjectDS150/wisconsin_population_density_2020.csv')

# Load County Geometries from the Census URL
counties_url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip"
gdf_counties = gpd.read_file(counties_url)

# Filter for Wisconsin only WI state Fips is 55
wi_counties = gdf_counties[gdf_counties['STATEFP'] == '55'].copy()

# Merge county shapes with population density data
wi_counties = wi_counties.merge(pop_df, left_on='NAME', right_on='County', how='left')
# Fill missing data with 0
wi_counties['Population_Density_PerSqMile'] = wi_counties['Population_Density_PerSqMile'].fillna(0)

# Convert Kwik Trip DataFrame to GeoDataFrame
kt_gdf = gpd.GeoDataFrame(
    kt_df, 
    geometry=gpd.points_from_xy(kt_df.Longitude, kt_df.Latitude),
    crs="EPSG:4326" # Standard WGS84 Coordinate System
)

# Set Coordinate Reference System (CRS)
wi_counties = wi_counties.to_crs(kt_gdf.crs)

# FIRST FILTER: Spatially join Kwik Trip points to Wisconsin counties 
# This ensures that ALL plotted points are within the state boundaries.
kt_gdf_wi_only = gpd.sjoin(kt_gdf, wi_counties[['geometry']], how='inner', predicate='intersects')

DANE_COUNTY_FIPS = '025'

# Filter County Shapes for Choropleth (Excluding Dane County polygon)
wi_counties_filtered = wi_counties[wi_counties['COUNTYFP'] != DANE_COUNTY_FIPS].copy()

# Filter Kwik Trip Points (Excluding locations in Dane County)
# 1. Get the geometry of Dane County
dane_geom = wi_counties[wi_counties['COUNTYFP'] == DANE_COUNTY_FIPS]['geometry'].iloc[0]

# 2. Filter out Kwik Trip locations that are within Dane County geometry, using the already filtered WI data
kt_gdf_filtered = kt_gdf_wi_only[~kt_gdf_wi_only.within(dane_geom)].copy()

# 4. GENERATE STATIC GEOGRAPHICAL PLOT FULL WISCONSIN PICTURE

fig_full, ax_full = plt.subplots(1, 1, figsize=(12, 12))

# 4a. Choropleth Map Uses ORIGINAL wi_counties data
wi_counties.plot(
    column='Population_Density_PerSqMile',
    cmap='YlOrRd', 
    legend=True,
    legend_kwds={
        'label': "Population Density (Per Sq Mile)",
        'orientation': "horizontal", 
        'shrink': 0.5, 
        'pad': 0.05,
        'format': "%.0f"
    },
    ax=ax_full,
    edgecolor='black',
    linewidth=0.5
)

# 4b. Scatter Plot of Kwik Trip Locations Uses ORIGINAL kt_gdf_wi_only data
kt_gdf_wi_only.plot(
    marker='o', 
    color='#03A9F4', 
    markersize=15, 
    ax=ax_full,
    zorder=2 
)

# Set map boundaries to full Wisconsin extent
minx, miny, maxx, maxy = wi_counties.total_bounds
ax_full.set_xlim(minx - 0.5, maxx + 0.5)
ax_full.set_ylim(miny - 0.5, maxy + 0.5)
ax_full.set_title('Wisconsin Population Density and Kwik Trip Locations (FULL Map)', fontsize=16)
ax_full.set_axis_off() 
plt.tight_layout()

#Saving and making sure it generates 
map_file_full = "wisconsin_density_kt_scatter_full.png"
plt.savefig(map_file_full, dpi=300)

print(f"Map (Full Wisconsin) successfully generated and saved to {map_file_full}")

