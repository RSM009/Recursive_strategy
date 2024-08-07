import socket  # Import the socket library for network communication
import os  # Import the os library for interacting with the operating system
import subprocess  # Import subprocess for executing system commands
# import Template_funct as tf  # Import a custom module named Template_funct
from datetime import datetime, timedelta  # Import datetime and timedelta for handling time
import multiprocessing  # Import multiprocessing for parallel processing
import random  # Import random for generating random numbers
import time  # Import time for time-related functions

def timeing():
    """
    Function to get the current local time in HH:MM:SS format.
    Returns:
        str: Current time formatted as "HH:MM:SS".
    """
    t = time.localtime()  # Get the current local time
    current_time = time.strftime("%H:%M:%S", t)  # Format the time as "HH:MM:SS"
    return current_time  # Return the formatted time


def main():
    """
    Main function to set up a server, accept client connections, and process incoming data.
    - Generates a random port number and writes it to "port.csv".
    - Creates a server socket to listen for incoming connections.
    - Processes incoming data to extract trading information and execute commands based on it.
    """
    # Generate a random port number between 8888 and 20000 and write it to "port.csv"
    with open("port.csv",'w') as file:
        x = str(random.randint(a=8888, b=20000))  # Generate random port number
        file.write(x)  # Write port number to file

    # Create a server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", int(x)))  # Bind the socket to the localhost and random port
    server_socket.listen(1)  # Listen for incoming connections (max 1 connection at a time)

    print("Server is listening...")  # Print status message
    client_socket, client_address = server_socket.accept()  # Accept a client connection

    print("Connection established with:", client_address)  # Print client address
    last_order_time = None  # Initialize variable to track the last order time
    
    while True:
        data = client_socket.recv(1024).decode()  # Receive data from client
        if not data:
            break  # Exit loop if no data is received
        
        now = datetime.now()  # Get the current time
        
        # Check if the time elapsed since the last order is less than 0.05 minutes (3 seconds)
        if last_order_time is not None and now - last_order_time < timedelta(minutes=0.05):
            data = "0"  # Set data to "0" if within the time limit
        
        parts = data.split('|')  # Split the received data by '|'
    
        # Initialize variables for extracted details
        symbol = None
        level_breached = None
        Level_breached_price = None
        Strike_price_gap = None
        user_defined_number = None
        
        # Extract details from the received data
        for part in parts:
            if part.startswith("symbol:"):
                symbol = part.split("symbol:")[1]
            elif part.startswith("level_breached:"):
                level_breached = int(part.split("level_breached:")[1])
            elif part.startswith("Level_breached_price:"):
                Level_breached_price = part.split("Level_breached_price:")[1]  
            elif part.startswith("Strike_Price_gap:"):
                Strike_price_gap = int(part.split("Strike_Price_gap:")[1])
            elif part.startswith("user_defined_number:"):
                user_defined_number = part.split("user_defined_number:")[1]
            elif part.startswith("breached_time:"):
                breached_time = part.split("breached_time:")[1]
        # Check if all required details are present
        if symbol and level_breached and Level_breached_price and Strike_price_gap is not None: 
            print(symbol, level_breached, Level_breached_price, Strike_price_gap, user_defined_number)
            print("Entered IN Trade ", timeing())  # Print trade entry time
            # # exit()        
            try:
                # Prepare command to execute the CE order script
                ce_command = f"python3.10 CE_PE_order_new.py {symbol} {level_breached} {Level_breached_price} {Strike_price_gap} {user_defined_number} {breached_time} >> {symbol}.txt"
                print(ce_command)
                # Execute the command
                x = os.system(ce_command)
                print("Command started successfully.")
                last_order_time = datetime.now()  # Update last order time
                data = "0"  # Reset data to "0"
                
            except Exception as e:
                print("Error:", e)  # Print error message if an exception occurs

if __name__ == "__main__":
    main()  # Run the main function if the script is executed directly
