# Import Libraries
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup # for HTML scraping
import requests # for HTML scraping
 
### Define General Functions ###

def get_dates():
    # Get the current date and time
    today = datetime.today().date()
    #print(f'current date = {today}')

    # Initalize start date
    # (need to match the dates selected for wind and solar generation)
    start_date = today - timedelta(days=32)
    #print(f'start date = {start_date}')

    # Initalize end date 
    # (need to match the dates selected for wind and solar generation)
    end_date = today - timedelta(days=2)
    #print(f'end date = {end_date}')

    # returns a timedelta object
    return start_date, end_date

# Get ERCOT API Access Token
def get_api_token():
    
    # Account Information 
    USERNAME = REMOVED""
    PASSWORD = REMOVED" "
    SUBSCRIPTION_KEY = REMOVED""

    # Authorization URL for signing into ERCOT Public API account
    AUTH_URL = "https://ercotb2c.b2clogin.com/ercotb2c.onmicrosoft.com/B2C_1_PUBAPI-ROPC-FLOW/oauth2/v2.0/token"

    # Data payload for POST request
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'grant_type': 'password',
        'scope': 'openid fec253ea-0d06-4272-a5e6-b478baeecd70 offline_access',
        'client_id': 'fec253ea-0d06-4272-a5e6-b478baeecd70',
        'response_type': 'id_token'
        }

    # Sign In/Authenticate
    auth_response = requests.post(AUTH_URL, data=data)

    # Retrieve access token
    access_token = auth_response.json().get("access_token")
    #print('Access token successfully retrieved!')

    return access_token, SUBSCRIPTION_KEY

def query_api(api_endpoint, params, access_token, SUBSCRIPTION_KEY):

    # Define headers
    headers = {
        "Authorization": "Bearer " + access_token,
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
        }

    # Send the GET request
    response = requests.get(api_endpoint, headers=headers, params=params)

    # Check if the request was successful
    
    # Parse the response as JSON
    if response.status_code == 200:
        raw_data = response.json()  
        #print('Data was successfully loaded')
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

    return raw_data

#### Queries ERCOT's API for wind and solar power generation data ####

def get_generation_dates():
    # Want the dates to look like:
    """ 
    posted date = the day the data were uploaded to the database
                  should be one day AFTER the delivery date
                  the time should be from 23:54 to 23:56 because the database is updated every hour on the 55th minute
        postedFrom = 2024-09-08T23:54:00
        postedTo = 2024-09-08T23:56:00

    delivery date = the day the data describes
                    should be one day BEFORE the delivery date
        deliveryDateFrom = 2024-09-07
        deliveryDateTo = 2024-09-07

    This setup ensures that all generation data for the delivery date exists in the database.
    If the delivery date was AFTER the posted date, then we would be looking into the future
    and the data would not exist (only forecast data, not actual)
    """

    start_date, end_date = get_dates()

    # Initalize posted date to yesterday
    posted_date = end_date + timedelta(days=1)
    #print(f'data was uploaded/posted on: {posted_date}')

    # Initalize delivery date to one day before posted date
    delivery_date = end_date
    #print(f'data corresponds to the date: {delivery_date}')

    # Set posted time from & to
    posted_time_from = 'T23:54:00'
    posted_time_to = 'T23:56:00'
    #print(f'posted time from {posted_time_from} to {posted_time_to}')

    # returns timedelta dates and string times
    return posted_date, delivery_date, posted_time_from, posted_time_to

def query_generation_data(api_endpoint, access_token, SUBSCRIPTION_KEY):
    
    posted_date, delivery_date, posted_time_from, posted_time_to = get_generation_dates()
    month_of_data = []

    # Get data for the past 30 days
    for i in range(31):    

        posted_dt_from = posted_date.strftime('%Y-%m-%d') + posted_time_from
        #print(f'posted dt from = {posted_dt_from}')

        posted_dt_to = posted_date.strftime('%Y-%m-%d') + posted_time_to
        #print(f'posted dt to = {posted_dt_to}')

        # Define parameters: want to extract just one day
        params = {
                "postedDatetimeFrom" : posted_dt_from,
                "postedDatetimeTo" : posted_dt_to,
                "deliveryDateFrom": delivery_date,
                "deliveryDateTo": delivery_date
                }

        day_of_data = query_api(api_endpoint, params, access_token, SUBSCRIPTION_KEY)
        #print(day_of_data)

        month_of_data.append(day_of_data)

        # update dates: go backwards in time
        posted_date -= timedelta(days=1)
        delivery_date -= timedelta(days=1)

        # Sleep to avoid hitting the rate limit (1 request per 2 seconds)
        time.sleep(2)
        if i%3==0:
            print(f'{i/30 * 100}% done extracting data...')
    
    print('################################\nSuccessfully extracted data from API\n')
    return month_of_data

def get_wind_data(access_token, SUBSCRIPTION_KEY):
    # Wind Power Production - Hourly Averaged Actual and Forecasted Values by Geographical Region
    api_endpoint = "https://api.ercot.com/api/public-reports/np4-742-cd/wpp_hrly_actual_fcast_geo"
    
    print('It will take approx. 1 minute to extract wind data\n################################')
    raw_wind_data = query_generation_data(api_endpoint, access_token, SUBSCRIPTION_KEY)

    return raw_wind_data

def get_solar_data(access_token, SUBSCRIPTION_KEY):
    # Solar Power Production - Hourly Averaged Actual and Forecasted Values by Geographical Region
    api_endpoint = "https://api.ercot.com/api/public-reports/np4-745-cd/spp_hrly_actual_fcast_geo"

    print('It will take approx. 1 minute to extract solar data\n################################')
    raw_solar_data = query_generation_data(api_endpoint, access_token, SUBSCRIPTION_KEY)

    return raw_solar_data

### Get the past 30 days of electricity grid load data from ERCOT's API ### 

def get_load_data(access_token, SUBSCRIPTION_KEY):
    # Define API Endpoint for Grid Load Data
    api_endpoint = "https://api.ercot.com/api/public-reports/np6-345-cd/act_sys_load_by_wzn"

    # Define parameters
    start_date, end_date = get_dates()
    params = {
        "operatingDayFrom": start_date.strftime('%Y-%m-%d'),
        "operatingDayTo": end_date.strftime('%Y-%m-%d'),
        }

    raw_load_data = query_api(api_endpoint, params, access_token, SUBSCRIPTION_KEY)
    print('Successfully extracted load data from API\n')

    return raw_load_data

###############################################
### Extract HTML Data on Electricity Prices ###
###############################################

## Define HTML Extraction Methods ##

## ****** add feedback messages to HTML extraction *******

# Generate list of dates to extract data from
def get_price_data_dates():
    start_date, _ = get_dates()
    date = start_date
    dates_list = []
    for i in range(31):
        dates_list.append(date.strftime('%Y%m%d'))
        date += timedelta(1)
    return dates_list

def scrape_price_data(date, api_endpoint):
    
    # Construct the URL by formatting the base URL with the date
    url = api_endpoint.format(date)
    
    # Open the webpage for the current date
    opened_webpage = requests.get(url)
    #print(f"Webpage for 2024-09-{date} opened successfully...")
    
    # Initialize a BeautifulSoup object to read and parse the webpage
    bs = BeautifulSoup(opened_webpage.content, "html.parser")
    #print(f"Webpage for 2024-09-{date} loaded and parsed successfully...")

    # Define an empty list where the data will be kept
    day_of_raw_data = []

    # Find all the tables in the webpage page that we have just parsed
    tables = bs.find_all("table")

    for table in tables:
        
        rows = table.find_all('tr')
        
        #Extract data from each cell in the row
        for row in rows:
            cells = row.find_all('td')
            single_hour = []
            # Only process rows that have <td> elements, skip <th> rows
            if len(cells) > 0:
                #row_data.append([cells[0].text.strip(), cells[1].text.strip(), cells[2].text.strip()])
                for cell in cells:
                    single_hour.append(cell.text.strip())
                day_of_raw_data.append(single_hour)
    
    return day_of_raw_data    

# The raw_price_data is formatted as nested lists. Each day (i.e., 12/18/2024) is a single list inside the main list. Each hour (i.e., 12/18/2024 at hour ending 11:00) is a list inside of the day.
# [ day1[ [hour1], [hour2], ..., [hour24] ],
#   day2[ [hour1], [hour2], ..., [hour24] ],
#   day3[ [hour1], [hour2], ..., [hour24] ],
#   ... 
# ]
def get_price_data():
    
    # Define the base URL with a placeholder for the date
    api_endpoint = "https://www.ercot.com/content/cdr/html/{}_dam_spp.html"

    # Generate list of past 30 days (just dd, not mm or yyyy) (strings)
    dates = get_price_data_dates()

    # Loop over each date, construct the URL, and extract data
    raw_price_data = []
    for date in dates:
        day = scrape_price_data(date, api_endpoint)
        raw_price_data.append(day)
    
    print('Successfully extracted price data\n')
    
    return raw_price_data