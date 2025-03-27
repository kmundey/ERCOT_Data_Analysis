### IMPORT LIBRARIES ###
import pandas as pd
from itertools import product

#######################
### GENERAL METHODS ###
#######################

# Flattens nested lists
def flatten_lists(raw_data):
    
    # Initialize the hourly_data_list, where each element will be a single hour from a single day (2D list)
    hourly_data_list = []
    
    #Loop through each element in list
    for elem in raw_data:

        # Flattens one day (1 row, 2D list) into 24 hours (24 rows, 1D lists)
        if len(elem) > 1:
            hourly_data_list.extend(elem)
        
        # If the date is missing data, add one empty list to represent 24 hours (will fix later)
        else:
            hourly_data_list.append(elem)
    
    return hourly_data_list

# Flattens nested dictionaries
def flatten_dictionaries(raw_data):
    
    # Flatten the nested dictionaries
    flattened_data = pd.json_normalize(raw_data)

    # Flatten 2D lists into 1D lists
    hourly_data_list = []
    for elem in flattened_data['data']:
        hourly_data_list.extend(elem)

    return hourly_data_list

# Creates a pandas DataFrame with the desired columns and corrects the datatypes for some columns
def create_df(hourly_data_list, all_cols, desired_cols):

    # Create dataframe
    df = pd.DataFrame(hourly_data_list, columns=all_cols)

    # Slice a copy of the dataframe and keep only desired columns
    df = df[desired_cols].copy()

    # Convert 'Date' column to datetime objects with NaTs for empty rows
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 

    # Extract values in 'Hour' column as an integer if needed (removes the :00)
    if df['Hour'].dtype == 'O' and df['Hour'].str.contains(':', na=False).any():
        df['Hour'] = df['Hour'].str.split(':').str[0]

    # Convert 'Hour' column to floats with NaNs for empty rows
    df['Hour'] = pd.to_numeric(df['Hour'], errors='coerce')

    return df

# Drop missing rows of data if they are in the first or last positions in the dataframe
def drop_missing_first_last_dates(df):
    
    # Track if any dates were removed
    removed_dates = False

    # Drop first row if missing data
    while pd.isnull(df['Date'].iloc[0]):
        df = df.iloc[1:]
        removed_dates = True
        print('The first day of data was missing. Removed date from the dataset')

    # Drop last row if missing data
    while pd.isnull(df['Date'].iloc[-1]):
        df = df.iloc[:-1]
        removed_dates = True
        print('The last day of data was missing. Removed date from the dataset')

    # Inform user of any changes to the date range
    if removed_dates:
        print(f"The new date range for the dataset is {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}\n")

    return df

# Add 24 new rows for each missing day of data (fill with correct date & hours, leave other data points as NaN)
def fill_missing_dates(df):
    
    # Create a complete date range
    date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='D')

    # Create a list of hours 1-24 (for reindexing)
    hours = list(range(1, 25))

    # Create a list of all possible missing date-time combinations (for reindexing)
    date_time_combos = list(product(date_range, hours))
    
    # Create dataframe for missing dates & times
    full_index = pd.DataFrame(date_time_combos, columns=['Date', 'Hour'])

    # Merge new dates & times with original index
    df = full_index.merge(df, on=['Date', 'Hour'], how='left')

    return df

# Fill empty rows of data with the historical average
def replace_with_historical_avg(df):

    # For feedback statement to user only
    missing_data = df[df.isna().any(axis=1)] # select rows with missing data
    missing_dates_list = missing_data['Date'].unique() # select dates with missing data
    missing_dates_list = [date.strftime('%Y-%m-%d') for date in missing_dates_list] # turn dates into list of strings
    
    # Iterate through columns and replace missing data w/ historical avg
    for column in list(df.columns):
        
        # Skip over Date and Hour columns
        if 'Date' not in column and 'Hour' not in column and 'Unnamed' not in column:
            
            # Calculate hourly avgs for the column
            hourly_avgs = df.groupby('Hour')[column].mean().round(2)

            # Fill missing values in the column
            df[column] = df[column].fillna(df['Hour'].map(hourly_avgs))

    # Inform user of changes
    print(f'Used historical averages to replace missing data on these dates:')
    for date in missing_dates_list:
        print(date[:10])

    return df

##############################
### ELECTRICITY PRICE DATA ###
##############################

def get_price_cols():
    
    # All column labels in the dataset
    all_cols = ['Date', 'Hour', 'Price_Bus_Avg', 'Price_Houston', 'Price_Hub_Avg', 'Price_North', 'Price_Panhandle', 
                  'Price_South', 'Price_West', 'LZ_AEN', 'LZ_CPS', 'LZ_HOUSTON', 'LZ-LCRA', 'LZ_NORTH', 'LZ_RAYBN', 'LZ_SOUTH', 
                  'LZ_WEST']
    
    # Only the desired columns to save
    desired_cols = ['Date', 'Hour', 'Price_Bus_Avg', 'Price_Houston', 'Price_Hub_Avg', 'Price_North', 
                    'Price_Panhandle', 'Price_South', 'Price_West']
    
    return all_cols, desired_cols

def transform_price_data(raw_price_data):

    # Flatten the data (3D list --> 2D list) so that each row represents one hour of data
    hourly_price_list = flatten_lists(raw_price_data)

    # Get dataframe columns
    all_cols, desired_cols = get_price_cols()

    # Create pandas DataFrame with desired columns and datatypes
    price_df = create_df(hourly_price_list, all_cols, desired_cols)
    
    # Handle missing dates and missing data points
    if price_df.isnull().values.any():

        # If first/last rows are missing data, drop rows
        price_df = drop_missing_first_last_dates(price_df)

        # Fill in any empty rows with the correct dates & hours
        price_df = fill_missing_dates(price_df)
    
        # Once empty rows have correct dates, fill missing data points via interpolation
        price_df = replace_with_historical_avg(price_df)

    # Sort rows by oldest date and hour to newest (ascending)
    price_df.sort_values(['Date', 'Hour'], inplace=True)

    return price_df

######################
### GRID LOAD DATA ###
######################

def get_load_cols():
    
    # All column labels in the dataset
    all_cols = ['Date', 'Hour', 'Load_Coast', 'Load_East', 'Load_FarWest', 'Load_North', 
                  'Load_CentralNorth', 'Load_South', 'Load_CentralSouth', 'Load_West', 'Load_Total', 'DST Flag']
    
    # Only the desired columns to save
    desired_cols = ['Date', 'Hour', 'Load_Coast', 'Load_East', 'Load_FarWest', 'Load_North', 
                    'Load_CentralNorth', 'Load_South', 'Load_CentralSouth', 'Load_West', 'Load_Total']
   
    return all_cols, desired_cols

def transform_load_data(raw_load_data):

    # Flatten the data (nested dictionaries --> 2D list) so that each row represents one hour of data
    hourly_load_list = flatten_dictionaries(raw_load_data)

    # Get dataframe columns
    all_cols, desired_cols = get_load_cols()

    # Create pandas DataFrame with desired columns and datatypes
    load_df = create_df(hourly_load_list, all_cols, desired_cols)

    # Handle missing dates and missing data points
    if load_df.isnull().values.any():

        # If first/last rows are missing data, drop rows
        load_df = drop_missing_first_last_dates(load_df)

        # Fill in any empty rows with the correct dates & hours
        load_df = fill_missing_dates(load_df)
    
        # Once empty rows have correct dates, fill missing data points via interpolation
        load_df = replace_with_historical_avg(load_df)

    # Sort rows by oldest date and hour to newest (ascending)
    load_df.sort_values(['Date', 'Hour'], inplace=True)
    
    return load_df

#############################
### SOLAR GENERATION DATA ###
#############################

def get_solar_cols():

    # All column labels in the dataset
    all_cols = ['DateTime', 'Date', 'Hour', 'Solar_SystemWide', 'COP_HSL_SYSTEM_WIDE', 'STPPF_SYSTEM_WIDE', 'PVGRPP_SYSTEM_WIDE', 
                'Solar_CenterWest', 'COP_HSL_CenterWest', 'STPPF_CenterWest', 'PVGRPP_CenterWest', 'Solar_NorthWest', 
                'COP_HSL_NorthWest', 'STPPF_NorthWest', 'PVGRPP_NorthWest', 'Solar_FarWest', 'COP_HSL_FarWest', 
                'STPPF_FarWest', 'PVGRPP_FarWest', 'Solar_FarEast', 'COP_HSL_FarEast', 'STPPF_FarEast', 'PVGRPP_FarEast', 
                'Solar_SouthEast', 'COP_HSL_SouthEast', 'STPPF_SouthEast', 'PVGRPP_SouthEast', 'Solar_CenterEast', 
                'COP_HSL_CenterEast', 'STPPF_CenterEast', 'PVGRPP_CenterEast', 'SYSTEM_WIDE_HSL', 'DSTFlag']
    
    # Only the desired columns
    desired_cols = ['Date', 'Hour', 'Solar_SystemWide', 'Solar_CenterWest', 'Solar_NorthWest', 'Solar_FarWest', 
                    'Solar_FarEast', 'Solar_SouthEast', 'Solar_CenterEast']

    return all_cols, desired_cols

def transform_solar_data(raw_solar_data):
    
    # Flatten the data (nested dictionaries --> 2D list) so that each row represents one hour of data
    hourly_solar_list = flatten_dictionaries(raw_solar_data)

    # Get dataframe columns
    all_cols, desired_cols = get_solar_cols()

    # Create pandas DataFrame with desired columns and datatypes
    solar_df = create_df(hourly_solar_list, all_cols, desired_cols)

    # Handle missing dates and missing data points
    if solar_df.isnull().values.any():

        # If first/last rows are missing data, drop rows
        solar_df = drop_missing_first_last_dates(solar_df)

        # Fill in any empty rows with the correct dates & hours
        solar_df = fill_missing_dates(solar_df)
    
        # Once empty rows have correct dates, fill missing data points via interpolation
        solar_df = replace_with_historical_avg(solar_df)

    # Sort rows by oldest date and hour to newest (ascending)
    solar_df.sort_values(['Date', 'Hour'], inplace=True)

    return solar_df

############################
### WIND GENERATION DATA ###
############################

def get_wind_cols():

    # All column labels in the dataset
    all_cols = ['DateTime', 'Date', 'Hour', 'Wind_SystemWide', 'COP_HSL_SYSTEM_WIDE', 'STWPF_SYSTEM_WIDE', 
                 'WGRPP_SYSTEM_WIDE', 'Wind_Panhandle', 'COP_HSL_Panhandle', 'STWPF_Panhandle', 'WGRPP_Panhandle', 
                 'Wind_Coast', 'COP_HSL_Coast', 'STPPF_Coast', 'WGRPP_Coast', 'Wind_South', 'COP_HSL_South', 
                 'STWPF_South', 'WGRPP_South', 'Wind_West', 'COP_HSL_West', 'STWPF_West', 'WGRPP_West', 
                 'Wind_North', 'COP_HSL_North', 'STWPF_North', 'WGRPP_North', 'SYSTEM_WIDE_HSL', 'DSTFlag' ]
    
    # Only the desired columns
    desired_cols = ['Date', 'Hour', 'Wind_SystemWide', 'Wind_Panhandle', 'Wind_Coast', 'Wind_South', 'Wind_West', 
                    'Wind_North']

    return all_cols, desired_cols

def transform_wind_data(raw_wind_data):
    
    # Flatten the data (nested dictionaries --> 2D list) so that each row represents one hour of data
    hourly_wind_list = flatten_dictionaries(raw_wind_data)

    # Get dataframe columns
    all_cols, desired_cols = get_wind_cols()

    # Create pandas DataFrame with desired columns and datatypes
    wind_df = create_df(hourly_wind_list, all_cols, desired_cols)

    # Handle missing dates and missing data points
    if wind_df.isnull().values.any():

        # If first/last rows are missing data, drop rows
        wind_df = drop_missing_first_last_dates(wind_df)

        # Fill in any empty rows with the correct dates & hours
        wind_df = fill_missing_dates(wind_df)

        wind_df = replace_with_historical_avg(wind_df)
    
        # Once empty rows have correct dates, fill missing data points via interpolation
        wind_df = replace_with_historical_avg(wind_df)

    # Sort rows by oldest date and hour to newest (ascending)
    wind_df.sort_values(['Date', 'Hour'], inplace=True)

    return wind_df