import pyotp  # Import the pyotp library for generating one-time passwords (OTPs) using Time-based One-Time Password (TOTP) algorithm

# Initialize the TOTP object with a secret key
totp = pyotp.TOTP('F45MPHSA4FFHU6E4665LT2565R4JI7K6')

# Generate a new OTP using the current time
key = totp.now()

# Print the generated OTP
print(key)

# Define user credentials and application-specific information
user_name = "FA65015"  # Username for authentication or identification
pwd = "Rajesh@29"  # Password for authentication

# Define additional variables for further use
factor2 = key  # Assign the generated OTP to factor2, which could be used for multi-factor authentication
vc = "FA65015_U"  # A variable likely used for a specific purpose, such as user identifier or verification code
app_key = "a7da79585cf0873082efd268f7fa47dd"  # Application-specific key, potentially used for API access or identification
imei = "abc1234"  # IMEI (International Mobile Equipment Identity) for a device, which might be used for device-specific operations

# Fyers API integration section

# Initialize another TOTP object with a different secret key specific to Fyers API
totp = "PT7PR6Z5XZ5H5VUWVJVY5FBCZGMDJVCD"  # Secret key for Fyers API
key_fyers = pyotp.TOTP(totp)  # Create a TOTP object using the Fyers API key
# print(key_fyers)
# Generate a new OTP using the current time for Fyers API
key_fyers = key_fyers.now()

# Define credentials for Fyers API
app_id = "QWL9SPROZZ-100"  # Application ID for accessing Fyers API
Secret_id = "JXIFL84HYX"  # Secret ID for accessing Fyers API
