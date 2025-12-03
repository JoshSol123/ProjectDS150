#Load Libraries IF THEY DONT LOAD IN MODULE you need to use *pip import* into the command terminal to load libraries into your computer  
import pandas as pd
import geopandas as gpd
import  folium as fm
import seaborn as sb
import matplotlib.pyplot as plt

kt_df = pd.read_csv('E:\Python\ProjectDS150\kwiktrip.csv')

pop_df = pd.read_csv('E:\Python\ProjectDS150\wisconsin_population_density_2020.csv')

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

#For histogram comparing pop density to counties. 
plt.figure(figsize=(10, 6))

sb.histplot(pop_df['Population_Density_PerSqMile'], bins=20, kde=True, color='skyblue', edgecolor='black')
plt.title('Distribution of Population Density in Wisconsin Counties (2020)')
plt.xlabel('Population Density (People per Sq Mile)')
plt.ylabel('Number of Counties')
plt.grid(axis='y', alpha=0.5)
plt.tight_layout()
plt.savefig("wisconsin_density_histogram.png")
print("Histogram saved as 'wisconsin_density_histogram.png'")