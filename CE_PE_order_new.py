import math
import time
from datetime import datetime
from datetime import date
from datetime import time
import datetime
from fyers_api import accessToken,fyersModel
import pyotp
import pandas as pd
import numpy as np
import yfinance as yf
import time
import csv
from calendar import calendar
import math
import time
import os
import sys
from NorenRestApiPy.NorenApi import  NorenApi
import login as lg
import yaml
import argparse
import requests as re 
from zipfile import ZipFile
from datetime import datetime

print("file started")
log_path =  str(os.getcwd())+"/"

def Shoonya_login():   
    """
    Handles login to the Shoonya API using provided credentials.
    Initializes the ShoonyaApiPy class from the NorenApi and performs the login
    using credentials (username, password, two-factor authentication code,
    vendor code, API secret, and IMEI). Prints a success message upon successful
    login or an error message and exits the script if login fails.
    """
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        
            global api
            api = self

    # import AppKit
    api = ShoonyaApiPy()

    #credentials
    user    = lg.user_name
    pwd     = lg.pwd
    factor2 = lg.factor2
    vc      = lg.vc
    app_key = lg.app_key
    imei    = lg.imei

    #make the api call
    # print(api)
    # ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
    # print(ret)
    try:
        ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
        # print(ret)
        print("Login successfully in Shoonya!")
    except Exception as e:
        
        print(f"Finvasia API FAILED: {e} ")
        sys.exit()

def download_and_save():
    """
    Downloads and extracts a ZIP file containing symbols data from the Shoonya API.
    Downloads a ZIP file from a specified URL, saves it to the current working directory,
    extracts its contents, and deletes the ZIP file afterward.
    """
    url = 'https://api.shoonya.com/NFO_symbols.txt.zip'
    # Current working directory
    save_folder = os.getcwd()
    
    # Extract file name from URL
    file_name = url.split('/')[-1]
    file_path = os.path.join(save_folder, file_name)

    # Download the file
    response = re.get(url)
    
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        # Extract ZIP file if needed
        if file_path.endswith('.zip'):
            with ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(save_folder)
            os.remove(file_path)  # Remove ZIP file after extraction
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        
                
def read_config(file_path):
    """
    Reads and parses a YAML configuration file.
    Opens and loads a YAML file from the given file_path, returning the configuration
    data as a dictionary.
    """    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def timestamp_to_date(timestamp):
    """
    Converts a Unix timestamp to a human-readable date string.
    Converts the given Unix timestamp into a datetime object and formats it as a
    string in the format "YYYY-MM-DD HH:MM:SS". Handles invalid timestamps by
    printing an error message.
    """
    try:
        date_object = datetime.datetime.fromtimestamp(timestamp)
        date_string = date_object.strftime("%Y-%m-%d %H:%M:%S")
        return date_string
    except ValueError:
        print("Invalid timestamp. Please provide a valid Unix timestamp.")
        return None
 
 
def round_nearest(n, r):
    """
    Rounds a number n to the nearest multiple of r.
    Uses the math.fmod function to calculate the remainder and adjust the number n
    to the nearest multiple of r.
    """
    return n - math.fmod(n, r)

def today_date():
    today = date.today()
    d1 = today.strftime("%d_%m_%Y") 
    d1 = str(d1)
    return d1


def timeing():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def start_date_for_ohlc():
    d = datetime.date.today()
    d += datetime.timedelta(-4)
    d = str(d)
    return d


def end_date_for_ohlc():
    d = datetime.date.today()
    d += datetime.timedelta(2)
    d = str(d)
    return d

def upcoming_expiry():
    d = datetime.date.today()
    while d.weekday() != 3:
        d += datetime.timedelta(1)
    d = str(d)
    d = d[8:]
    # print("upcoming :",d)
    return d


def year():
    d = datetime.date.today()
    while d.weekday() != 3:
        d += datetime.timedelta(1)
    d = str(d)
    d = d[2:4]
    d = str(d)
    return d

def current_month():
    d = datetime.date.today()
    while d.weekday() != 3:
        d += datetime.timedelta(1)
    d = str(d)
    d = d[5:7]
    d = int(d)
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    moth = d - 1
    curr_mon = months[moth]
    curr_mon = str(curr_mon)
    return curr_mon


def mon():
    d = datetime.date.today()
    while d.weekday() != 3:
        d += datetime.timedelta(1)
    d = str(d)
    d = d[5:7]
    d = str(d)
    d = int(d)
    return d

def give_approx_delta():
    d = datetime.date.today()
    x = int(d.weekday())
    approx_del = 300-x * 50 
    if x == 4:
        approx_del = 200
    return approx_del
 
def place_order_buy(x, qt, price, pt, trig_price):
    """
    Places a buy order for a given trading symbol.
    Uses the Shoonya API to place a buy order with specified parameters (symbol, quantity,
    price type, price, trigger price) and handles exceptions if the order placement fails.
    """
    print(x, qt)
    try:
        # Place a Buy Order
        orders = api.place_order(
            buy_or_sell='B',
            product_type='M',
            exchange='NFO',
            tradingsymbol=x,
            quantity=qt, 
            discloseqty=0,
            price_type=pt,
            price=price, 
            trigger_price=trig_price,
            retention='DAY', 
            remarks='strategy')
        
    except Exception as e:
        orders = None
        print("Exception when calling OrderApi->place_order_buy: %s\n" % e)
         
    return orders

def place_order_sell(x, qt):
    """
    Places a sell order for a given trading symbol.
    Uses the Shoonya API to place a sell order with specified parameters (symbol, quantity)
    and handles exceptions if the order placement fails.
    """
    try:
        # Place a Sell Order
        orders = api.place_order(
            buy_or_sell='S',
            product_type='M',
            exchange='NFO',
            tradingsymbol=x,
            quantity=qt, 
            discloseqty=0,
            price_type='MKT', 
            trigger_price=None,
            retention='DAY', 
            remarks='strategy')
        
    except Exception as e:
        orders = None
        print("Exception when calling OrderApi->place_order_sell: %s\n" % e)         
    return orders
def clean_symbol(symbol):
    """
    Cleans the stock symbol by removing specific substrings.
    
    Args:
    symbol (str): The stock symbol to be cleaned.

    Returns:
    str: The cleaned stock symbol.
    """
    # Check if 'NSE:' exists in the symbol and remove it
    if 'NSE:' in symbol:
        symbol = symbol.replace('NSE:', '')
    # Check if '-EQ' exists in the symbol and remove it
    if '-EQ' in symbol:
        symbol = symbol.replace('-EQ', '')
    if '50-INDEX' in symbol:
        symbol = symbol.replace('50-INDEX', '')
    if '-INDEX' in symbol:
        symbol = symbol.replace('-INDEX', '')    
        
    return symbol

def extract_ohlc_time(data):
    ohlc_data = []
    for candle in data["candles"]:
        timestamp = candle[0]
        timestamp  = timestamp_to_date(timestamp=timestamp)
        open_price = candle[1]
        high_price = candle[2]
        low_price = candle[3]
        close_price = candle[4]
        ohlc_data.append((timestamp, open_price, high_price, low_price, close_price))
    df = pd.DataFrame(ohlc_data, columns=["Timestamp", "Open", "High", "Low", "Close"])
    df = df.reset_index(drop=True)
    return df

def get_access_token():
    client_id = lg.app_id
    secret_key = lg.Secret_id
    redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
    grant_type = "authorization_code"
    response_type = "code"
    if not os.path.exists("access_token.txt"):
        session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type='code', grant_type='authorization_code')
        response = session.generate_authcode()
        print("login url:-",response)
        auth_code = input("Enter auth code:-")
        session.set_token(auth_code)
        accesstoken = session.generate_token()['access_token']
        with open("access_token.txt","w") as f:
            f.write(accesstoken)
    else:
        with open("access_token.txt","r") as f:
            accesstoken = f.read()
    return accesstoken   

def get_NIFTY_LTP_price():
    fyers = fyersModel.FyersModel(client_id=lg.app_id,token = get_access_token(),log_path=log_path)
    data = {
    "symbols":"NSE:NIFTY50-INDEX"
    }
    response = fyers.quotes(data=data)
    lp_value = response['d'][0]['v']['lp']
    LTP = lp_value -lp_value % 50
    return LTP

def get_derivative_LTP_price(token, symbol, pe_ce, strike):
    """
    Retrieves the Last Traded Price (LTP) for a specific derivative.
    
    Args:
    token (str): Token for the derivative.
    symbol (str): The symbol of the derivative.
    pe_ce (str): Put or Call option type.
    strike (float): Strike price of the derivative.

    Returns:
    float: The Last Traded Price (LTP).
    """
    token = get_Token(symbol)
    data = api.get_quotes(exchange="NFO", token=token)
    
    for key, value in data.items():
        if key == 'lp':
            return value

def OHLCHistory():
    try:
        fyers = fyersModel.FyersModel(client_id=lg.app_id,token = get_access_token(),log_path=log_path)
    except Exception as e:
        print(f"fyers api failed{e}")
    data = {
        "symbol":"NSE:NIFTY50-INDEX",
        "resolution":"1",
        "date_format":"1",
        "range_from":start_date_for_ohlc(),
        "range_to":end_date_for_ohlc(),
        "cont_flag":"1"
    }
    response = fyers.history(data=data)
    response = extract_ohlc_time(response)
    data = {
    "symbols":"NSE:NIFTY50-INDEX"
    }
    ltp_response = fyers.quotes(data=data)
    last_row_index = response.index[-1]
    desired_value = ltp_response['d'][0]['v']['lp']
    response.iat[last_row_index, response.columns.get_loc('Close')] = desired_value
    return response

def get_Token(word):
    li = 'None'
    with open('NFO_symbols.txt','r') as f:
        lines = f.readlines()
    for line in lines:
        if line.find(word) != -1:
            li = list(line.split(","))
            li = li[1]       
    return li

def order_report():
    try:
        rep = api.get_order_book()
    except Exception as e:
        print(f"order_report:{e}")
    df = pd.DataFrame(rep)
    df = df['norenordno']
    df = df[0]
    return int(df)

def get_qt(pri,fund_allocation=100): 
    try:
        rep = api.get_limits()
        rep = rep['cash']
    except Exception as e:
        print(f"Getting quantity Failed:{e}")
    rep = rep * fund_allocation
    qt = rep/pri 
    qt = round_nearest(qt,50)
    return qt                               


def trade_status(orderno):
    try:
        rep = api.get_order_book()
    except Exception as e:
        print(f"order_report:{e}")
    
    df = 0
    for i in rep:
        if i['norenordno'] == orderno:
            df = i['status']
    return str(df)



def sell_trade_status():
    try:
        rep = api.get_order_book()
    except Exception as e:
        print(f"api.get_order_book Failed:{e}")
    df = pd.DataFrame(rep)
    sig = 0
    state = df["status"]
    state = state[0]
    typ =df["trantype"]
    typ = typ[0]  
    if (state == 'COMPLETE' or state == 'CANCELED'):
        if typ == "S" :
            sig =  1
    return sig


def get_avg_exec(orderno):        
    orderno = str(orderno)
    try:
        rep = api.get_order_book()
        
    except Exception as e:
        print(f"api.get_order_book Failed:{e}")
    df = 0
    for i in rep:
        print(f"get_order_book:{i} -",rep)
        if i['norenordno'] == orderno:
            df = i['avgprc']
    return df

def get_order_no(symbol):
    rep = api.get_order_book()
    for i in rep:
        if i['tsym'] == str(symbol):
            num = i["norenordno"]
            return num     

def Order_Status(od_no):
    x = api.get_order_book()
    print(type(x))
    for i in x:
        if i['norenordno'] == str(od_no):
            status = i["status"]
            return status     

def search_and_find_upcoming_expiry(api, exchange, query):
    ret = api.searchscrip(exchange=exchange, searchtext=query)

    if ret and 'values' in ret:
        symbols = ret['values']
        expiry_dates = []
        
        for symbol in symbols:
            tsym = symbol['tsym']
            expiry_str = tsym[-7:]  # Extract the last 7 characters (DDMMMYY)

            try:
                expiry_date = datetime.strptime(expiry_str, "%d%b%y")
                expiry_dates.append((expiry_date, symbol['token']))
            except ValueError:
                continue

        if expiry_dates:
            # Find the nearest future expiry date
            upcoming_expiry = min((date for date in expiry_dates if date[0] > datetime.now()), default=None)
            if upcoming_expiry:
                expiry_date, token = upcoming_expiry
                print(f"Upcoming expiry date: {expiry_date.strftime('%d-%b-%Y')}, Token: {token}")
            else:
                print("No upcoming expiry date found.")
        else:
            print("No expiry dates extracted.")
    else:
        print("No symbols found.")    

def update_levels_csv(entered_level, to_next_level):
    # Define the CSV file name
    csv_file = 'levels.csv'
    
    # Check if the file exists
    if not os.path.isfile(csv_file):
        # If the file does not exist, create an empty DataFrame with the required columns
        df = pd.DataFrame(columns=['entered_level', 'to_next_level', 'cycle_count'])
        df.to_csv(csv_file, index=False)  # Create the file with the columns
        print("CSV file created with columns: entered_level, to_next_level, cycle_count")
    else:
        # Load the CSV file into a DataFrame
        df = pd.read_csv(csv_file)
        
        # Check if the DataFrame is empty and has no columns
        if df.empty or df.columns.size == 0:
            # Handle the case where the file is empty or has no columns
            df = pd.DataFrame(columns=['entered_level', 'to_next_level', 'cycle_count'])
            df.to_csv(csv_file, index=False)  # Reset the file with the columns
            print("CSV file was empty or incorrectly formatted; reset with columns: entered_level, to_next_level, cycle_count")

    # Determine the next cycle count
    if not df.empty and 'cycle_count' in df.columns:
        last_cycle_count = df['cycle_count'].iloc[-1]
        new_cycle_count = last_cycle_count + 1
    else:
        new_cycle_count = 1  # Start with 1 if the DataFrame is empty or column is missing

    # Add a new row with the given values and the incremented cycle count
    new_row = pd.DataFrame([{
        'entered_level': entered_level,
        'to_next_level': to_next_level,
        'cycle_count': new_cycle_count
    }])
    
    # Concatenate the new row to the existing DataFrame
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

    print(f"Updated CSV file with: entered_level={entered_level}, to_next_level={to_next_level}, cycle_count={new_cycle_count}")

def get_user_defined_number(config_file, target_symbol):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    for stock in config['stocks']:
        if stock['symbol'] == target_symbol:
            return stock['user_defined_number']
    return None
  
def get_quantity(config_file, target_symbol):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    for stock in config['stocks']:
        if stock['symbol'] == target_symbol:
            return stock['quantity']
    return None
  
  

def main():
    # Create a parser to handle command-line arguments
    parser = argparse.ArgumentParser(description='Process some integers.')
    
    # Define the arguments that the script expects
    parser.add_argument('symbol', type=str, help='The stock symbol')
    parser.add_argument('level_breached', type=int, help='The level breached')
    parser.add_argument('Level_breached_price', type=float, help='The price at which the level was breached')
    parser.add_argument('Strike_price_gap', type=float, help='The gap between strike prices')
    parser.add_argument('user_defined_number', type=float, help='A user-defined number for adjustment')  
    parser.add_argument('breached_time', type=str, help='The time at which the level was breached')
    # Parse the command-line arguments
    args = parser.parse_args()

    # Extract the values from the parsed arguments
    symbol = args.symbol
    level_breached = args.level_breached
    Level_breached_price = args.Level_breached_price
    Strike_price_gap = args.Strike_price_gap
    user_defined_number = args.user_defined_number
    breached_time = args.breached_time
    
    
    content = read_config('detail.yaml')
    user_defined_number  = get_user_defined_number('detail.yaml', symbol)
    qt = get_quantity('detail.yaml', symbol)  # Quantity to trade
    # Print the values to check
    print('symbol:', symbol, 'level_breached:', level_breached, 'Level_breached_price:', Level_breached_price, 'Strike_price_gap:', Strike_price_gap)
   
    # Simulate login and data download
    Shoonya_login()
    download_and_save()
    
    # Read configuration settings from a file
    strike_price_pe = strike_price_ce = None
    
    # Calculate the strike prices based on the configuration and arguments
    if str(content['Strike_Type']) == 'ATM':
        strike_price_pe = strike_price_ce = int(Level_breached_price / Strike_price_gap) * int(Strike_price_gap)
    elif str(content['Strike_Type']) == 'ITM':
        strike_price_ce = int(Level_breached_price / Strike_price_gap) * int(Strike_price_gap) - int(user_defined_number)
        strike_price_pe = int(Level_breached_price / Strike_price_gap) * int(Strike_price_gap) + int(user_defined_number)
    
    # Generate the symbol names for the options
    if 'NIFTY50-INDEX' in symbol:
        symbol_ce = clean_symbol(symbol) + str(content['Upcoming_expiry_NIfty']) + 'C' + str(strike_price_ce)
        symbol_pe = clean_symbol(symbol) + str(content['Upcoming_expiry_NIfty']) + 'P' + str(strike_price_pe)
    elif 'NIFTYBANK-INDEX' in symbol:
        symbol_ce = "BANKNIFTY" + str(content['Upcoming_expiry_BankNifty']) + 'C' + str(strike_price_ce)
        symbol_pe = "BANKNIFTY" + str(content['Upcoming_expiry_BankNifty']) + 'P' + str(strike_price_pe)
    elif 'FINNIFTY-INDEX' in symbol:
        symbol_ce = clean_symbol(symbol) + str(content['Upcoming_expiry_FinNifty']) + 'C' + str(strike_price_ce)
        symbol_pe = clean_symbol(symbol) + str(content['Upcoming_expiry_FinNifty']) + 'P' + str(strike_price_pe)
    elif 'MIDCPNIFTY-INDEX' in symbol:
        symbol_ce = clean_symbol(symbol) + str(content['Upcoming_expiry_MidCapNifty']) + 'C' + str(strike_price_ce)
        symbol_pe = clean_symbol(symbol) + str(content['Upcoming_expiry_MidCapNifty']) + 'P' + str(strike_price_pe)
    elif '-EQ' in symbol:
        symbol_ce = clean_symbol(symbol) + str(content['Upcoming_expiry_EQ']) + 'C' + str(strike_price_ce)
        symbol_pe = clean_symbol(symbol) + str(content['Upcoming_expiry_EQ']) + 'P' + str(strike_price_pe)

    # Get tokens for the options
    print(symbol_ce, symbol_pe)
    ce_token = get_Token(word=symbol_ce)
    pe_token = get_Token(word=symbol_pe)
    
    # Print tokens for debugging

       
    x_ce = place_order_buy(x=symbol_ce, qt=qt, price=0, pt='MKT', trig_price=None)
    ce_od_no = x_ce['norenordno']
    y_pe = place_order_buy(x=symbol_pe, qt=qt, price=0, pt='MKT', trig_price=None)
    pe_od_no = y_pe['norenordno']
    
    # Initialize price and order number variables
    ce_open_pos = pe_open_pos = 1
    update_flag_pe = update_flag_ce = 0
    ce_new_od_no = pe_new_od_no = 0
    ce_new_price_exec = ce_price_exec = get_derivative_LTP_price(token=ce_token, symbol=symbol_ce, pe_ce="CE", strike=str(strike_price_ce))
    pe_new_price_exec = pe_price_exec = get_derivative_LTP_price(token=ce_token, symbol=symbol_ce, pe_ce="CE", strike=str(strike_price_ce))
    
    print(f"CE Price Executed: {ce_price_exec}, PE Price Executed: {pe_price_exec}")

    # Target and stoploss values from configuration
    target_CE_PE = user_defined_number * content['target_factor']
    stoploss_CE_PE = user_defined_number * content['stoploss_factor']
    
    # Loop until the market closes
    while datetime.now().time() < datetime.strptime('23:15:00', '%H:%M:%S').time():
        print("Entered the while loop")
        
        try:
            # Calculate target and stoploss prices
            val1 = float(ce_new_price_exec) - float(stoploss_CE_PE) * 0.98
            val2 = float(pe_new_price_exec) - float(stoploss_CE_PE) * 0.98
            val3 = float(ce_new_price_exec) + float(target_CE_PE) * 0.98
            val4 = float(pe_new_price_exec) + float(target_CE_PE) * 0.98

            print(f"CE stoploss : {val1}, PE stoploss: {val2}, CE target: {val3}, PE target: {val4}", time.time())

            # Get the latest prices
            current_CE_price = get_derivative_LTP_price(token=ce_token, symbol=symbol_ce, pe_ce="CE", strike=str(strike_price_ce))
            current_PE_price = get_derivative_LTP_price(token=pe_token, symbol=symbol_pe, pe_ce="PE", strike=str(strike_price_pe))

            # Update executed prices if trades are complete
            if trade_status(ce_new_od_no) :
                ce_new_price_exec = get_derivative_LTP_price(token=ce_token, symbol=symbol_ce, pe_ce="CE", strike=str(strike_price_ce))
                
            if trade_status(pe_new_od_no) :
                pe_new_price_exec = get_derivative_LTP_price(token=pe_token, symbol=symbol_pe, pe_ce="PE", strike=str(strike_price_pe)) 
                
            # Check if stoploss or target levels are hit and place new orders if needed
            if float(current_CE_price) <= val1:
                print("CE stoploss hit")
                # place_order_sell(x=symbol_ce, qt=qt)
                trig_price = float(ce_price_exec) * 0.99 
                trig_price = round_nearest(trig_price, 0.05)
                print(symbol_ce, qt, ce_price_exec, "SL-LMT", trig_price)
                x = place_order_buy(symbol_ce, qt=qt, price=ce_new_price_exec, pt="SL-LMT", trig_price=trig_price)
                ce_new_price_exec = get_derivative_LTP_price(token=ce_token, symbol=symbol_ce, pe_ce="CE", strike=str(strike_price_ce))                
                ce_new_od_no = x["norenordno"]  
            
            elif float(current_PE_price) <= val2:
                print("PE stoploss hit")
                # place_order_sell(x=symbol_pe, qt=qt)
                trig_price = (float(pe_price_exec) * 0.99)
                trig_price = round_nearest(trig_price, 0.05)
                print(symbol_pe, qt, pe_price_exec, "SL-LMT", trig_price)
                y = place_order_buy(symbol_pe, qt=qt, price=pe_new_price_exec, pt="SL-LMT", trig_price=trig_price)
                pe_new_price_exec = get_derivative_LTP_price(token=pe_token, symbol=symbol_pe, pe_ce="PE", strike=str(strike_price_pe))
                # pe_new_od_no = y["norenordno"]
                
            elif float(current_CE_price) >= val3 :
                print("CE target hit")
                update_levels_csv(entered_level=ce_new_price_exec, to_next_level=current_CE_price,symbol=symbol)
                api.cancel_order(orderno=pe_new_od_no)
                print("PE order cancelled")
                update_flag_ce = 1
                target_CE_PE += user_defined_number * content['target_factor']
                stoploss_CE_PE -= user_defined_number *  content['stoploss_factor']
                print("target_CE_PE", target_CE_PE)
                
            elif float(current_PE_price) >= val4 :
                print("PE target hit")
                update_levels_csv(entered_level=pe_new_price_exec, to_next_level=current_PE_price)
                api.cancel_order(orderno=ce_new_od_no)
                print("CE order cancelled")
                target_CE_PE += user_defined_number *  content['target_factor']
                stoploss_CE_PE -= user_defined_number * content['stoploss_factor']
                print("target_CE_PE", target_CE_PE)
                
            else:
                print(f"CE Price: {current_CE_price}, PE Price: {current_PE_price}")
                time.sleep(3)  # Wait a bit before checking again
        
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)  # Wait a bit before retrying in case of an error
                
        

if __name__ == "__main__":
    main()
    