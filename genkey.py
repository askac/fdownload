import pyotp
import qrcode
import random
import string
import os
import argparse
import base64

def generate_random_secret(length=16):
    """Generate a random secret key"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_qr_code(secret, issuer_name, account_name, interval=30):
    """Generate a QR code for the TOTP"""
    totp = pyotp.TOTP(secret, interval=interval)
    provisioning_uri = totp.provisioning_uri(name=account_name, issuer_name=issuer_name)
    qr = qrcode.make(provisioning_uri)
    qr_filename = f"{account_name}_qr.png"
    qr.save(qr_filename)
    return qr_filename

def save_secret_to_file(secret, filename="appkey.py"):
    """Save the secret key to a Python file"""
    with open(filename, "w") as f:
        f.write(
            f'# Generated by genkey.py. Do not edit manually.\n'
            f'# Use genkey.py to regenerate this file.\n\n'
            f'SECRET_KEY = "{secret}"\n'
        )

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code for a TOTP secret key")
    parser.add_argument("issuer_name", help="The issuer name for the TOTP")
    parser.add_argument("account_name", help="The account name for the TOTP")
    args = parser.parse_args()

    issuer_name = args.issuer_name
    account_name = args.account_name

    # Check if issuer_name and account_name are valid
    if not issuer_name or not account_name:
        print("Error: Issuer name and account name must be provided.")
        return

    if len(account_name) < 3:
        print("Error: Account name must be at least 3 characters long.")
        return

    # Generate a random secret key
    secret = generate_random_secret()
    encoded_secret = base64.b32encode(secret.encode('utf-8')).decode('utf-8')
    print(f"Generated Secret Key: {encoded_secret}")

    # Save the secret key to appkey.py
    save_secret_to_file(encoded_secret)

    # Generate the QR code
    qr_filename = generate_qr_code(encoded_secret, issuer_name, account_name, interval=30)
    print(f"QR code saved as: {qr_filename}")

    # Open the QR code image
    #if os.name == "posix":
    #    os.system(f"open {qr_filename}")
    #else:
    #    os.system(f"start {qr_filename}")

if __name__ == "__main__":
    main()
