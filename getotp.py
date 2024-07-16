import pyotp
import time
import appkey

SECRET_KEY = appkey.SECRET_KEY

# Function to generate TOTP with a custom time window
def generate_totp(secret_key, interval=30):  # Ensure the interval is 60 seconds
    totp = pyotp.TOTP(secret_key, interval=interval)
    return totp.now()

if __name__ == '__main__':
    custom_interval = 30  # Set the TOTP interval to 60 seconds
    while True:
        current_totp = generate_totp(SECRET_KEY, interval=custom_interval)
        print(f"Current TOTP: {current_totp}")
        print(f"This TOTP is valid for the next {custom_interval} seconds.")
        time.sleep(custom_interval)
