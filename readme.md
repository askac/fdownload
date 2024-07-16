## README.md

# WSGI TOTP Authenticated File Server

This repository contains a WSGI application for TOTP-based authenticated file access. The following components are included:

- `app.py`: The main application file.
- `appkey.py`: The generated secret key file.
- `flist.txt`: The list of files available for access.
- `genkey.py`: A script for generating the secret key and QR code.
- `getotp.py`: A script for checking TOTP using a command-line interface.
- `index.html`: The client HTML interface.

## Functionality and Workflow of `app.py`

The `app.py` file contains the main application logic for TOTP-based authentication and file access. The functionality is divided into several endpoints:

### 1. Authentication Endpoint
**URL:** `/auth`  
**Method:** `POST`  
**Description:** Authenticates a user by verifying their TOTP token.

**Request Payload:**
```json
{
    "username": "user",
    "totp_token": "123456"
}
```

**Response:**
- On success:
  ```json
  {
      "message": "Authentication successful"
  }
  ```
- On failure:
  ```json
  {
      "error": "Invalid TOTP token"
  }
  ```

### 2. List Files Endpoint
**URL:** `/files`  
**Method:** `POST`  
**Middleware:** `totp_required('/files')`  
**Description:** Returns a list of files that match the search term.

**Request Payload:**
```json
{
    "totp_token": "123456",
    "search_term": "example"
}
```

**Response:**
- On success:
  ```json
  {
      "files": [
          {
              "hash": "abc123",
              "name": "example.txt",
              "base_path": "/path/to/file",
              "type": "Type",
              "display_name": "Type: example.txt"
          }
      ]
  }
  ```
- On failure:
  ```json
  {
      "error": "No matching files found"
  }
  ```

### 3. Download File Endpoint
**URL:** `/download`  
**Method:** `POST`  
**Middleware:** `totp_required('/download')`  
**Description:** Allows downloading a file by verifying the provided file hash.

**Request Payload:**
```json
{
    "totp_token": "123456",
    "file_hash": "abc123"
}
```

**Response:**
- On success: The file will be sent as an attachment.
- On failure:
  ```json
  {
      "error": "File not found"
  }
  ```

### 4. Static Files Endpoint
**URL:** `/`  
**Method:** `GET`  
**Description:** Serves the `index.html` file to the client.

**Workflow:**
1. **Authentication:** The user authenticates by sending a `POST` request to `/auth` with their username and TOTP token.
2. **Listing Files:** After successful authentication, the user can search for files by sending a `POST` request to `/files` with their TOTP token and search term.
3. **Downloading Files:** The user can download a file by sending a `POST` request to `/download` with their TOTP token and the file hash.

## `genkey.py` Usage

The `genkey.py` script is used to generate a new secret key and corresponding QR code for TOTP authentication.

### Command-Line Arguments
- `--issuer`: The name of the service or company issuing the TOTP (required).
- `--account_name`: The account name associated with the TOTP (required).

### Example Usage
To generate a new secret key and QR code:

```sh
python genkey.py --issuer "MyService" --account_name "user@example.com"
```

### Output
- The script will generate a new secret key and save it in `appkey.py`.
- A QR code will be displayed for scanning with an authenticator app.

### `genkey.py` Script Description
- **Imports:** Necessary libraries for TOTP and QR code generation.
- **Secret Key Generation:** Generates a base32-encoded secret key.
- **QR Code Generation:** Creates a QR code URL using the provided issuer and account name.
- **QR Code Display:** Displays the QR code for the user to scan with an authenticator app.
- **Key Storage:** Saves the generated secret key to `appkey.py`.

## `getotp.py` Usage

The `getotp.py` script is used to generate and display the current TOTP code for verification purposes.

### Example Usage
To generate the current TOTP code:

```sh
python getotp.py
```

### Output
- The script will print the current TOTP code to the console.
- The script will also display the time remaining until the TOTP code expires.

## `flist.txt` Format

The `flist.txt` file contains the list of file lists available for search. Each line represents a file list and its type, separated by a comma.

### Example Format
```
dir_a/list_a.txt,Type Alpha
dir_b/list_b.txt,Type Beta
```

Each line in `flist.txt` specifies:
1. The path to a file containing a list of accessible files (`list_a.txt`, `list_b.txt`, etc.).
2. The type or category of files contained in the list (e.g., "Type Alpha", "Type Beta").

### List File Format

Each file listed in `flist.txt` (e.g., `list_a.txt`, `list_b.txt`) contains a list of file paths that are accessible. These paths are relative to the directory containing the list file.

### Example of `dir_a/list_a.txt`
```
files/path/to/storage/file001.bin
files/path/to/storage/file002.bin
```

For instance, if `flist.txt` contains:
```
dir_a/list_a.txt,Type Alpha
```

And `dir_a/list_a.txt` contains:
```
files/path/to/storage/file001.bin
files/path/to/storage/file002.bin
```

The full path to `file001.bin` would be:
```
dir_a/files/path/to/storage/file001.bin
```

### Important Notes
- Ensure that the paths in the list files are relative to the directory of the list file itself.
- The paths in the list files should point to the actual files you want to make available for search and download.

## `index.html`

The `index.html` file is the client interface for interacting with the application. It allows users to authenticate, search for files, and download files.

### Features
- **Authentication Form:** Allows the user to enter their username and TOTP token for authentication.
- **File Search Form:** Allows the user to enter a search term to search for files.
- **File List Display:** Displays the list of matching files with download buttons.

By following the instructions and using the provided scripts and files, you can set up and run the TOTP authenticated file server to securely access files.