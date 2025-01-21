import pandas as pd
import numpy as np
from pathlib import Path

# Merges all dataframes into a single dataframe
def merge_df(price_df, load_df, wind_df, solar_df):

    # Merge data into a single df
    merged_df = pd.merge(price_df, load_df, on=['Date', 'Hour_Ending'], how='outer') # merge first two df
    merged_df = pd.merge(merged_df, wind_df, on=['Date', 'Hour_Ending'], how='outer') # merge third df
    merged_df = pd.merge(merged_df, solar_df, on=['Date', 'Hour_Ending'], how='outer') # merge fourth df

    # Convert 24th hour to 0th hour and then convert into an int
    merged_df['Hour_Ending'] = merged_df['Hour_Ending'].replace(24.0, 0.0)
    merged_df['Hour_Ending'] = merged_df['Hour_Ending'].apply(np.int64)

    return merged_df

# Saves CSV to clean_data folder
def save_as_CSV(df):
    
    # Define the directories
    curr_directory = Path(__file__).resolve().parent
    clean_data_directory = curr_directory.parent / "clean_data"

    # Create the folder if it doesn't exist
    clean_data_directory.mkdir(parents=True, exist_ok=True)

    # Define relative path to clean_data folder
    path = clean_data_directory / "ERCOT_Electricity_Data.csv"

    # Save the CSV
    df.to_csv(path, index=False)
    print(f"CSV saved to: {path}\n")