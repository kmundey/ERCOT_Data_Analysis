# Import modules
import extract_transform_load.extract as extract
import extract_transform_load.transform as transform
import extract_transform_load.load as load

### EXTRACT DATA###
# Extracts past 30 days of raw data on the ERCOT electricity grid

# Extract data from an ERCOT HTML webpage: "https://www.ercot.com/content/cdr/html/{date}_dam_spp.html"
raw_price_data = extract.get_price_data() # Electrical bus prices across ERCOT regions

# Get Access Token and Subscription Key to ERCOT's API
access_token, SUBSCRIPTION_KEY = extract.get_api_token() 

# Extract data from across ERCOT regions using ERCOT's API
raw_load_data = extract.get_load_data(access_token, SUBSCRIPTION_KEY) # mW of electricity demand
raw_wind_data = extract.get_wind_data(access_token, SUBSCRIPTION_KEY) # mW of wind energy generation
raw_solar_data = extract.get_solar_data(access_token, SUBSCRIPTION_KEY) # mW of solar energy generation


### TRANSFORM DATA ##
# Normalizes and cleans each dataset into Pandas dataframe

price_df = transform.transform_price_data(raw_price_data)
load_df = transform.transform_load_data(raw_load_data)
wind_df = transform.transform_wind_data(raw_wind_data)
solar_df = transform.transform_solar_data(raw_solar_data)


### LOAD DATA ### 
merged_df = load.merge_df(price_df, load_df, wind_df, solar_df)
load.save_as_CSV(merged_df)