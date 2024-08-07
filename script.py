import subprocess
import login as lg
from fyers_api import accessToken
import os 

# Define the paths to your two scripts
script1 = 'order_placer.py'
script2 = 'excel_prep.py'

# Run the first script in parallel
process1 = subprocess.Popen(['python3.10', script1])

# Define the function to get access token
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

get_access_token()

# Run the second script in parallel
process2 = subprocess.Popen(['python3.10', script2])

# Wait for both processes to complete
process1.wait()
process2.wait()

print("Both scripts have completed.")
