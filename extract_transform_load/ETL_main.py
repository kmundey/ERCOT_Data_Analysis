# Import modules
import extract_data
import trash_folder.transform_data_OLD as transform_data_OLD
import load_data

### EXTRACT DATA###
# Extracts past 30 days of raw data on the ERCOT electricity grid

# Extract data from an ERCOT HTML webpage: "https://www.ercot.com/content/cdr/html/{date}_dam_spp.html"
raw_price_data = extract_data.get_price_data() # Electrical bus prices across ERCOT regions

# Get Access Token and Subscription Key to ERCOT's API
access_token, SUBSCRIPTION_KEY = extract_data.get_api_token() 

# Extract data from across ERCOT regions using ERCOT's API
raw_load_data = extract_data.get_load_data(access_token, SUBSCRIPTION_KEY) # mW of electricity demand
raw_wind_data = extract_data.get_wind_data(access_token, SUBSCRIPTION_KEY) # mW of wind energy generation
raw_solar_data = extract_data.get_solar_data(access_token, SUBSCRIPTION_KEY) # mW of solar energy generation


### TRANSFORM DATA ##
# Normalizes and cleans each dataset into Pandas dataframe

price_df = transform_data_OLD.transform_price_data(raw_price_data)
load_df = transform_data_OLD.transform_load_data(raw_load_data)
wind_df = transform_data_OLD.transform_wind_data(raw_wind_data)
solar_df = transform_data_OLD.transform_solar_data(raw_solar_data)


### LOAD DATA ### 
merged_df = load_data.merge_df(price_df, load_df, wind_df, solar_df)
load_data.save_as_CSV(merged_df)