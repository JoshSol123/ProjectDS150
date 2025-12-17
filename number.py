# Load Libraries
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sb
import sys
import os

# Define constant for square meters to square miles conversion
SQ_M_TO_SQ_MI = 2589988.11
# Define an equal-area CRS (Albers Equal Area Conic) for accurate area calculation
ALBERS_CRS = 'EPSG:5070' 
    kt_df = pd.read_csv('E:/Python/ProjectDS150/kwiktrip.csv')
    pop_df = pd.read_csv('E:/Python/ProjectDS150/wisconsin_population_density_2020.csv')

    # Load County Geometries from the Census URL
    counties_url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip"
    gdf_counties = gpd.read_file(counties_url)

    # Filter for Wisconsin only (STATEFP == '55')
    wi_counties = gdf_counties[gdf_counties['STATEFP'] == '55'].copy()

    # Merge county shapes with population density data
    wi_counties = wi_counties.merge(pop_df, left_on='NAME', right_on='County', how='left')
    wi_counties['Population_Density_PerSqMile'] = wi_counties['Population_Density_PerSqMile'].fillna(0)

    # Convert Kwik Trip DataFrame to GeoDataFrame
    kt_gdf = gpd.GeoDataFrame(
        kt_df, 
        geometry=gpd.points_from_xy(kt_df.Longitude, kt_df.Latitude),
        crs="EPSG:4326" # Standard WGS84 Coordinate System
    )

# Ensure county geometry is in the same CRS as the points for spatial join
wi_counties = wi_counties.to_crs(kt_gdf.crs)

MILWAUKEE_COUNTY_NAME = 'Milwaukee'
wi_counties = wi_counties[wi_counties['NAME'] != MILWAUKEE_COUNTY_NAME].copy()
# Project to an equal-area CRS for accurate area calculation
wi_counties_proj = wi_counties.to_crs(ALBERS_CRS) 
wi_counties['Area_sq_meters'] = wi_counties_proj.geometry.area
wi_counties['Area_sq_miles'] = wi_counties['Area_sq_meters'] / SQ_M_TO_SQ_MI

# Spatial join to link each store to its county's name
kt_county_join = gpd.sjoin(kt_gdf, wi_counties[['NAME', 'geometry']], how='inner', predicate='intersects')

# Group by county name and count the stores
kt_counts = kt_county_join.groupby('NAME').size().reset_index(name='KwikTrip_Count')

# Select core columns from the geographical data
correlation_df = wi_counties[['NAME', 'Population_Density_PerSqMile', 'Area_sq_miles']].copy()

# Merge in the store counts
correlation_df = correlation_df.merge(kt_counts, on='NAME', how='left')
correlation_df['KwikTrip_Count'] = correlation_df['KwikTrip_Count'].fillna(0) # Counties with no KTs get 0

# Calculate the final Kwik Trip Density (Stores per Square Mile)
correlation_df['KwikTrip_Density_PerSqMi'] = (
    correlation_df['KwikTrip_Count'] / correlation_df['Area_sq_miles']
)

# Optional: Calculate the correlation coefficient
correlation_value = correlation_df['Population_Density_PerSqMile'].corr(
    correlation_df['KwikTrip_Density_PerSqMi']
)

plt.figure(figsize=(10, 7))

# Use seaborn's regplot to create a scatter plot and fit a linear regression model
sb.regplot(
    data=correlation_df,
    x='Population_Density_PerSqMile',
    y='KwikTrip_Density_PerSqMi',
    scatter_kws={'alpha': 0.7, 'color': '#03A9F4'},  # Kwik Trip Blue
    line_kws={'color': 'red'},
    ci=95  # Show 95% confidence interval
)

plt.title(
    f'Correlation: Kwik Trip Density vs. Population Density in WI Counties\n'
    f'(Excluding Milwaukee Co.) (R-value: {correlation_value:.2f})', 
    fontsize=14
)
plt.xlabel('Population Density (People per Sq Mile)')
plt.ylabel('Kwik Trip Density (Stores per Sq Mile)')
plt.grid(axis='both', alpha=0.5)
plt.tight_layout()

correlation_file = "wi_density_correlation_plot_no_milwaukee.png"
plt.savefig(correlation_file)

print(f"Correlation plot successfully generated and saved to {correlation_file}")

