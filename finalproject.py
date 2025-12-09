#Load Libraries IF THEY DONT LOAD IN MODULE you need to use *pip import* into the command terminal to load libraries into your computer  
import pandas as pd
import geopandas as gpd
import  folium
import seaborn as sb
import matplotlib.pyplot as plt
from folium.features import GeoJsonTooltip

kt_df = pd.read_csv('E:/Python/ProjectDS150/kwiktrip.csv')

pop_df = pd.read_csv('E:/Python/ProjectDS150/wisconsin_population_density_2020.csv')

#All Counties url
counties_url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip"
#Read the file through Geopandas
gdf_counties = gpd.read_file(counties_url)
#To get specifically wisconsin, I needed  to get the fips number which is 55 and filter to only wisconsin
wi_counties = gdf_counties[gdf_counties['STATEFP'] == '55'].copy()

#This is connecting the county shape data to the population data by county NAME and County on Pop_df
wi_counties = wi_counties.merge(pop_df, left_on='NAME', right_on='County', how='left')
#There shouldn't be any but needed to fill any missing data values to zero as the map wasnt working without it
wi_counties['Population_Density_PerSqMile'] = wi_counties['Population_Density_PerSqMile'].fillna(0)

# Convert Kwik Trip data to a GeoDataFrame
kt_gdf = gpd.GeoDataFrame(
    kt_df, 
    geometry=gpd.points_from_xy(kt_df.Longitude, kt_df.Latitude),
    crs="EPSG:4326" # Standard WGS84 Coordinate System
)

wi_counties = wi_counties.to_crs(kt_gdf.crs)
kt_gdf_wi_only = gpd.sjoin(kt_gdf, wi_counties[['geometry']], how='inner', predicate='intersects')

m = folium.Map(location=[44.5, -89.5], zoom_start=7, tiles='CartoDB Positron')

# Create a simplified Pandas DataFrame containing only the data columns needed for the tooltip
# The GeoJsonTooltip object expects a simple dictionary/list structure for its data parameter.
# By creating a dictionary from the relevant columns, we ensure it's JSON serializable.
density_data_dict = wi_counties[['NAME', 'Population_Density_PerSqMile']].set_index('NAME').to_dict()['Population_Density_PerSqMile']


# A. Base Layer: Population Density Choropleth
# This colors the county polygons.

# Create the Choropleth layer
choropleth = folium.Choropleth(
    # NOTE: geo_data should be the GeoJSON geometry source (wi_counties)
    geo_data=wi_counties, 
    name='Population Density Choropleth',
    # NOTE: data should be the simple mapping of ID (County Name) to Value (Density)
    data=wi_counties,
    columns=['NAME', 'Population_Density_PerSqMile'],
    key_on='feature.properties.NAME',
    fill_color='YlOrRd', # Yellow -> Orange -> Red (Red = High Density)
    fill_opacity=0.7,
    line_opacity=0.3,
    legend_name='Population Density (Per Sq Mile) - 2020 Census',
    highlight=True # Highlight county on hover
).add_to(m)

# Add an interactive tooltip to display the county name and density on hover
# Crucial Fix: We pass only the necessary column names to GeoJsonTooltip 
# and let Folium handle the mapping to the GeoJSON features.
choropleth.geojson.add_child(
    GeoJsonTooltip(
        fields=['NAME', 'Population_Density_PerSqMile'],
        aliases=['County:', 'Density (per sq mi):'],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid grey;
            border-radius: 3px;
            box-shadow: 3px;
        """
    )
)

# B. Overlay Layer: Individual Kwik Trip Stores as Points
# We iterate through the Kwik Trip GeoDataFrame (kt_gdf) and add a marker for each store.
kt_group = folium.FeatureGroup(name='Kwik Trip Store Locations').add_to(m)

for idx, row in kt_gdf_wi_only.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3, 
        color='#03A9F4', 
        fill=True,
        fill_color='#03A9F4',
        fill_opacity=1.0,
        popup=f"Kwik Trip Store: {row.get('Address', 'Location Details')}" 
    ).add_to(kt_group)



# C. Add Controls and Save

# Add layer control so you can toggle the layers (density map and store points)
folium.LayerControl().add_to(m)

# Save the map as an interactive HTML file
output_file = "wisconsin_kwik_trip_density_map.html"
m.save(output_file)

#For histogram comparing pop density to counties. 
plt.figure(figsize=(10, 6))

sb.histplot(pop_df['Population_Density_PerSqMile'], bins=20, kde=True, color='skyblue', edgecolor='black')
plt.title('Distribution of Population Density in Wisconsin Counties (2020)')
plt.xlabel('Population Density (People per Sq Mile)')
plt.ylabel('Number of Counties')
plt.grid(axis='y', alpha=0.5)
plt.tight_layout()
plt.savefig("wisconsin_density_histogram.png")

