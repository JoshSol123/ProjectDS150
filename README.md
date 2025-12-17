### This project aims to talk about the correlation between Population Density and Number of Kwik Trips in a given County of Wisconsin. The goal is to visualize the density and points and calculate a regression model in order to get the actual correlation percentage (R squared) using python libraries like pandas, geopandas, seaborn, and Matplotlib.

Depending on how you start. You must have the libraries downloaded to your pc. Command prompt pip import pandas will get the library to work on your own pc
txt file for kwik trip is in the repository 
Steps for creating a filter on the csv kwik trip data
1) Connect local paths to a variable for each csv (pop density 2020 and Kwiktrip.csv) (This was my path for the code use your personal computer or hub where the files are) 
kt_df = pd.read_csv('E:/Python/ProjectDS150/kwiktrip.csv')
pop_df = pd.read_csv('E:/Python/ProjectDS150/wisconsin_population_density_2020.csv')
2) Load in the county geometry data for visualizations later using Census.gov tiger files counties_url = "https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_county_20m.zip"
gdf_counties = gpd.read_file(counties_url)
3) To filter counties in the US to ONLY Wisconsin. Use the STATEFP column and filter to '55' as that is WI state FIPS code : wi_counties = gdf_counties[gdf_counties['STATEFP'] == '55'].copy()
4) Merge the county shapefile with the population density data (For better organization and connection) using .merge and use .fillna for any missing data : wi_counties = wi_counties.merge(pop_df, left_on='NAME', right_on='County', how='left'): wi_counties['Population_Density_PerSqMile'] = wi_counties['Population_Density_PerSqMile'].fillna(0)
5) In order for the kwik trip data to work. It must user the latitude longitude data to connect back to the county shapefile and population data. Meaning The kwik trip data must be turned into a Geodataframe using Geopandas : kt_gdf = gpd.GeoDataFrame(
    kt_df, 
    geometry=gpd.points_from_xy(kt_df.Longitude, kt_df.Latitude),
    crs="EPSG:4326" # Standard WGS84 Coordinate System
)
Making sure to the Coordinate Reference Systems are the same between variables set the wi_counties and kt geodataframe (gdf) by using .to_crs of the kwik trip gdf
6) If you want to take out DANE COUNTY. The county fips code is 025 using that to filter the Wi_county data by column COUNTYFP and if you want to get rid of any specific county this method can be used with any county  :wi_counties_filtered = wi_counties[wi_counties['COUNTYFP'] != DANE_COUNTY_FIPS].copy()

7) To generate the geographical plot we are going to use .plot thorugh matplotlib.pyplots (plt) and make sure using all of the variables inside the .plot function in order to make the figure look good. (Title , x,y labels, set_limitsx and y to make each graph limited in its highest max) (I found using .tightlayout also helps in making the graaph organized in a neat png.)
8) Then saving through .savefig in plt
9) For the density correlation, we need to calculate the area in a way that avoids the distortions caused by projecting a 3D globe onto a 2D surface. We do this by converting to  Albers Equal Area Conic projection with geopandas, which will ensure accurate measurements are preserved regardless of where you are in Wisconsin.
10) We use seaborns regplot methnod to create a linear regressison plot. Seaborn will make a scatter plot, and then apply a best fit line and coefficient of determination, or the R value. We use the correlation df for our data, KwikTrip density on the y-axis as it's our dependent variable, and have population density on the y-axis. We use ci=95 as our confidence interval, which will appear as a shaded region on the graph. Because we removed Milwaukee, our graph won't be highly skewed by its insane population density relative to the rest of Wisconsin and it's lack of stores. 
