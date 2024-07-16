import os
import sys

# Ensure the current directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from flask import Flask, request, jsonify, send_file, send_from_directory, abort
import pyotp
import time
import hashlib
import csv
from appkey import SECRET_KEY  # Import the generated secret key

application = Flask(__name__)

# Application home directory
AppHomeDir = os.path.dirname(__file__)

# Session window and TOTP interval
TOTP_INTERVAL = 30  # TOTP code valid for 30 seconds
TOTP_VALID_WINDOW = 4  # Allow 1 time window before and after

# File list path
FILE_LIST_PATH = os.path.join(AppHomeDir, 'flist.txt')

# Read the file list
def read_file_list():
    file_list = []
    with open(FILE_LIST_PATH, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            file_list.append((row[0], row[1]))
    return file_list

# Generate SHA256 hash for a given file path
def generate_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()

# Verify TOTP token
def verify_totp(totp_token):
    totp = pyotp.TOTP(SECRET_KEY, interval=TOTP_INTERVAL)
    print(f"Now: {totp.now()} Test: {totp_token}")
    return totp.verify(totp_token, valid_window=TOTP_VALID_WINDOW)

# Search for files in the listed files and return their hashes
def search_files_in_list(search_term):
    matched_files = []
    for list_file, file_type in read_file_list():
        list_file_path = os.path.join(AppHomeDir, list_file)
        if os.path.exists(list_file_path):
            base_path = os.path.dirname(list_file_path)
            with open(list_file_path, 'r') as f:
                for line in f:
                    file_path = line.strip()
                    if search_term in file_path:
                        file_hash = generate_hash(os.path.join(base_path, file_path))
                        matched_files.append({
                            'hash': file_hash,
                            'name': file_path,
                            'base_path': base_path,
                            'type': file_type,
                            'display_name': f"{file_type}: {os.path.basename(file_path)}"
                        })
    return matched_files

# Authentication endpoint
@application.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()
    if not data or 'username' not in data or 'totp_token' not in data:
        return jsonify({'error': 'Missing username or totp_token'}), 400
    
    totp_token = data['totp_token']
    
    if verify_totp(totp_token):
        return jsonify({'message': 'Authentication successful'}), 200
    else:
        print(f"Invalid TOTP token.")
        return jsonify({'error': 'Invalid TOTP token'}), 403

# Middleware to check TOTP token
def totp_required(endpoint_name):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if not request.json or 'totp_token' not in request.json:
                return jsonify({'message': 'Missing TOTP token'}), 403
            
            totp_token = request.json['totp_token']
            
            if not verify_totp(totp_token):
                return jsonify({'message': 'Invalid or expired TOTP token'}), 403
            
            return f(*args, **kwargs)
        wrapped_function.__name__ = f.__name__
        application.add_url_rule(endpoint_name, endpoint_name, wrapped_function, methods=['POST'])
        return wrapped_function
    return decorator

# List files endpoint
@application.route('/files', methods=['POST'])
@totp_required('/files')
def list_files():
    data = request.get_json()
    if not data or 'search_term' not in data:
        return jsonify({'error': 'Missing search_term'}), 400
    
    search_term = data['search_term']
    
    if len(search_term) < 6:
        return jsonify({'error': 'Search term must be at least 6 characters long'}), 400
    
    matched_files = search_files_in_list(search_term)
    
    if not matched_files:
        return jsonify({'error': 'No matching files found'}), 404

    return jsonify({'files': matched_files}), 200

# Download file endpoint
@application.route('/download', methods=['POST'])
@totp_required('/download')
def download_file():
    data = request.get_json()
    if not data or 'file_hash' not in data:
        return jsonify({'error': 'Missing file_hash'}), 400
    
    file_hash = data['file_hash']
    
    matched_files = search_files_in_list('')  # Get all files with hashes
    file_dict = {file['hash']: file for file in matched_files}
    
    if file_hash not in file_dict:
        return jsonify({'error': 'File not allowed'}), 403
    
    file_info = file_dict[file_hash]
    full_path = os.path.join(file_info['base_path'], file_info['name'])
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(full_path, as_attachment=True, download_name=os.path.basename(file_info['name']))

# Serve static files
@application.route('/')
def index():
    return send_from_directory(AppHomeDir, 'index.html')

if __name__ == '__main__':
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    application.run(debug=True)
