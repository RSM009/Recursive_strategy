import pandas as pd
from fyers_api import fyersModel
from fyers_api import accessToken
import yaml
from datetime import datetime as dt
from fyers_apiv3 import fyersModel
import datetime as datetime
import pandas as pd
import csv
import os 
import time
from datetime import timedelta
import socket
import login as lg
import threading

# Global variables
breached = False
UPDATE_INTERVAL = 5

# Connect to the local server
with open("port.csv",'r') as file:
    x = file.read()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", int(x)))
message = "Connected "
client_socket.send(message.encode())    
log_path = str(os.getcwd()) + "/"
current_minute = None
current_candle = None

# Function to get access token
def get_access_token():
    """
    Retrieves the access token for the Fyers API. 
    If the access token is not already available in 'access_token.txt', 
    it initiates a session to obtain a new one.
    """
    client_id = lg.app_id
    secret_key = lg.Secret_id
    redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
    grant_type = "authorization_code"
    response_type = "code"
    
    if not os.path.exists("access_token.txt"):
        session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type='code', grant_type='authorization_code')
        response = session.generate_authcode()
        print("login url:-", response)
        auth_code = input("Enter auth code:-")
        session.set_token(auth_code)
        accesstoken = session.generate_token()['access_token']
        with open("access_token.txt", "w") as f:
            f.write(accesstoken)
    else:
        with open("access_token.txt", "r") as f:
            accesstoken = f.read()
    return accesstoken   

# Function to read YAML configuration
def read_config(file_path):
    """
    Reads the YAML configuration file and returns the contents as a Python dictionary.
    """
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Function to get start date for OHLC data
def start_date_for_ohlc():
    """
    Returns the start date for the OHLC (Open, High, Low, Close) data in epoch format.
    The start date is set to 3 days before the current date.
    """
    d = datetime.date.today() + datetime.timedelta(0)
    start_datetime = datetime.datetime.combine(d, datetime.time.min)
    epoch = int(time.mktime(start_datetime.timetuple()))
    return epoch

# Function to get end date for OHLC data
def end_date_for_ohlc():
    """
    Returns the end date for the OHLC (Open, High, Low, Close) data in epoch format.
    The end date is set to the current date.
    """
    d = datetime.date.today()
    end_datetime = datetime.datetime.combine(d, datetime.time.max)
    epoch = int(time.mktime(end_datetime.timetuple()))
    return epoch

def print_current_candle_time():
    """
    Print the current time in HH:MM:SS format.
    """
    # Get the current time
    now = dt.now()
    
    # Format the time as HH:MM:SS
    current_time_str = now.strftime("%H:%M")
    
    # Print the formatted time
    return current_time_str
    # print(f"Current candle time: {current_time_str}") 
# Function to extract OHLC data and convert to DataFrame
def extract_ohlc_time(data):
    """
    Extracts OHLC (Open, High, Low, Close) data from the response and converts it into a Pandas DataFrame.
    """
    ohlc_data = []
    for candle in data["candles"]:
        timestamp = candle[0]
        timestamp = timestamp_to_date(timestamp=timestamp)
        open_price = candle[1]
        high_price = candle[2]
        low_price = candle[3]
        close_price = candle[4]
        ohlc_data.append((timestamp, open_price, high_price, low_price, close_price))
    df = pd.DataFrame(ohlc_data, columns=["Timestamp", "Open", "High", "Low", "Close",])
    df = df.reset_index(drop=True)
    return df

# Function to initialize Fyers API
def initialize_fyers(client_id, secret_key, redirect_uri):
    """
    Initializes the Fyers API session using provided credentials.
    """
    session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type='code', grant_type='authorization_code')
    response = session.auth()
    token = response['access_token']
    return fyersModel.FyersModel(client_id=client_id, token=token)

# Function to convert timestamp to human-readable date
def timestamp_to_date(timestamp):
    """
    Converts a Unix timestamp to a human-readable date string.
    """
    try:
        date_object = datetime.datetime.fromtimestamp(timestamp)
        date_string = date_object.strftime("%Y-%m-%d %H:%M:%S")
        return date_string
    except ValueError:
        print("Invalid timestamp. Please provide a valid Unix timestamp.")
        return None

# Function to clean symbol names
def clean_symbol(symbol):
    """
    Cleans the symbol string by removing 'NSE:' and '-EQ' prefixes if they exist.
    """
    if 'NSE:' in symbol:
        symbol = symbol.replace('NSE:', '')
    if '-EQ' in symbol:
        symbol = symbol.replace('-EQ', '')
        
    return symbol

# Function to get historical data
def get_historical_data(fyers, symbol):
    """
    Retrieves historical data for the specified symbol using the Fyers API.
    """
    data = {
        "symbol": symbol,
        "resolution": "1",
        "date_format": "0",
        "range_from": start_date_for_ohlc(),
        "range_to": end_date_for_ohlc(),
        "cont_flag": "1"
    }
    response = fyers.history(data=data)
    return response

# Function to calculate price levels
def calculate_levels(open_price, user_defined_number):
    """
    Calculates price levels based on the open price and user-defined number.
    """
    levels = {}
    for i in range(10, 0, -1):
        levels[f'Level -{i}'] = open_price - (i * user_defined_number)
    levels['Level 0'] = open_price
    for i in range(1, 11):
        levels[f'Level +{i}'] = open_price + (i * user_defined_number)
    return levels

# Function to send order messages
def order_message_sender(msg):
    """
    Sends an order message to the connected socket.
    """
    client_socket.send(msg.encode()) 

# Function to update the breached level
def update_breached_level(symbol):
    """
    Updates the breached level for the given symbol based on live price data.
    """
    df = pd.read_excel('stock_levels.xlsx')
    row_index = df[df["Symbol"] == symbol].index
    prv_level = df.at[row_index[0], "Current_Level"]
    Strike_price_gap = df.at[row_index[0], "Strike_price_gap"]
    level_breached = int((df.at[row_index[0], "Live_Price"] - df.at[row_index[0], "Day_Open_Price"]) / df.at[row_index[0], "User_Code"]) 
    Level_breached_price = df.at[row_index[0], "Live_Price"] + level_breached * df.at[row_index[0], "User_Code"]
    user_defined_number = df.at[row_index[0], "User_Code"]
    
    if int(prv_level) != int(level_breached): 
        msg = f"symbol:{symbol}|level_breached:{level_breached}|Level_breached_price:{Level_breached_price}|Strike_Price_gap:{Strike_price_gap}|user_defined_number:{user_defined_number}|breached_time:{print_current_candle_time()}"
        breached = True
        print("msg:-", msg)
        order_message_sender(msg=msg)
        df.at[row_index[0], "Current_Level"] = level_breached
        df.to_excel('stock_levels.xlsx', index=False, engine='openpyxl')
    else: 
        print("No level breached")
    return level_breached

# Function to update live price
def Update_Live_price(symbol, fyers):
    """
    Updates the live price of the specified symbol in the Excel file.
    """
    try:
        data = {
            "symbols": symbol
        }
        response = fyers.quotes(data=data)
        lp_value = response['d'][0]['v']['lp']
        curr_price = float(lp_value)  # Ensure curr_price is a float

        df = pd.read_excel('stock_levels.xlsx', engine='openpyxl')
        row_index = df[df["Symbol"] == symbol].index
        
        if not row_index.empty:  # Check if the index is not empty
            df.at[row_index[0], "Live_Price"] = curr_price
            df.to_excel('stock_levels.xlsx', index=False, engine='openpyxl')
        else:
            print(f"Symbol {symbol} not found in the DataFrame.")

    except Exception as e:
        print("Failed to update live price:", e)
# Function to save data to an Excel file
def save_to_excel(data, file_path):
    """
    Saves the given data to an Excel file at the specified path.
    """
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False, engine='openpyxl')


# Main function
def main():
    config = read_config('config.yaml')
    client_id = ""
    
    get_access_token()
    file_path = 'access_token.txt'
    with open(file_path, 'r') as file:
        content = file.read()  
    access_token = content
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
    all_data = []
      
    
    for stock in config['stocks']:
        
        symbol = stock['symbol']
        # print("symbol:-",symbol)    
        user_defined_number = stock['user_defined_number']
        Strike_price_gap = stock['Strike_price_gap']
        hist_data = get_historical_data(fyers, symbol)
        candle_data = extract_ohlc_time(hist_data)
        # print(candle_data)
        
        starting_candle_time = str(datetime.datetime.today()).split()[0] + " " + str("09:15:00")

        starting_candle_data_open = candle_data['Open'].iloc[0]
        starting_candle_data_close = candle_data['Close'].iloc[0]
        # print(starting_candle_data_open,starting_candle_data_close)
        if starting_candle_data_open is not None:
            levels = calculate_levels(starting_candle_data_open, user_defined_number)
            # level_breached = int((df.at[row_index[0], "Live_Price"] - df.at[row_index[0], "Day_Open_Price"])/df.at[row_index[0], "User_Code"]) 
            Current_Level =  int(starting_candle_data_close - starting_candle_data_open)/user_defined_number
            Current_Level = round(Current_Level)
            stock_data = {
                'Symbol': symbol,
                'Day_Open_Price': starting_candle_data_open,
                'User_Code': user_defined_number,
                'Live_Price': starting_candle_data_close,
                'Current_Level': Current_Level, 
                'Strike_price_gap': Strike_price_gap
            }
           
            
            stock_data.update(levels)
            all_data.append(stock_data)
            save_to_excel(all_data, 'stock_levels.xlsx')
        else:
                print(f"Failed to fetch historical data for {symbol}")

        while not breached  :
                Update_Live_price(symbol,fyers) 
                update_breached_level(symbol)
                time.sleep(UPDATE_INTERVAL)
        
                
        
        else:
            print(" NO Level breached")    

# Run the script
if __name__ == "__main__":
    main()
