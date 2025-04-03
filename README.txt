###########################
### Using the ERCOT API ###
###########################

    - Create an account at: www.
    - Add your username, password, and subscription key to 'extract_data.py' 

    --> extract_transform_load
        --> extract_data.py
            --> line 28: get_api_token()
                    # Account Information 
                    USERNAME = "fill in"
                    PASSWORD = "fill in"
                    SUBSCRIPTION_KEY = "fill in"

########################
### Data Description ###
########################

a. Price Data: Electrical bus prices across ERCOT regions ($/MWh)

Description: 

    Date --> The YYYY-MM-DD associated with the data (datetime object)
    Hours --> The hour ending when the data were collected (int)
    Price_Bus_Avg --> 
    Price_Houston --> 
    Price_Hub_Avg --> 
    Price_North --> 
    Price_Panhandle --> 
    Price_South --> 
    Price_West --> 

b. Load Data: mW of electricity demand

Description: 

    Date --> The YYYY-MM-DD associated with the data (datetime object)
    Hours --> The hour ending when the data were collected (int)
    Load_Coast
    Load_East
    Load_FarWest
    Load_North
    Load_CentralNorth
    Load_South
    Load_CentralSouth
    Load_West
    Load_Total

c. Solar Generation Data: mW of solar electricity generated

Description: This report is posted every hour and includes System-wide and geographic regional hourly averaged 
solar power production, STPPF, PVGRPP, and COP HSL for On-Line PVGRs for a rolling historical 48-hour period as 
well as the system-wide and regional STPPF, PVGRPP, and COP HSL for On-Line PVGRs for the rolling future 
168-hour period. System-wide and regional generation, are included in this report under column labels with 
"GEN_" prefixes. ERCOT's forecasts attempt to predict HSL, which is uncurtailed power generation potential. 
Since generation is impacted by curtailments, the data in this report should not be used to evaluate forecast 
performance. Steps will be taken to include HSL in this report in the future.

    Date --> The YYYY-MM-DD associated with the data (datetime object)
    Hours --> The hour ending when the data were collected (int)


d. Wind Generation Data: mW of wind electricity generated

Description: This report is posted every hour and includes System-wide and Geographic Regional actual hourly 
averaged wind power production, STWPF, WGRPP and COP HSLs for On-Line WGRs for a rolling historical 48-hour 
period as well as the System-wide and Regional STWPF, WGRPP and COP HSLs for On-Line WGRs for the rolling future 
168-hour period. Our forecasts attempt to predict HSL, which is uncurtailed power generation potential. Actual 
system-wide generation, which is included in this report as "ACTUAL_SYSTEM_WIDE" or "SYSTEM_WIDE" is impacted by 
curtailments. Because of this, the data in this report should not be used to evaluate forecast performance. Steps 
will be taken to include Actual System-wide HSL in this report in the future.

    Date --> The YYYY-MM-DD associated with the data (datetime object)
    Hours --> The hour ending when the data were collected (int)
