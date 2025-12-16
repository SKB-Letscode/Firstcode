
#====================================================================================
# Author: Sara 
# Created on: 11 Dec 2025
# Brief: This script uses google drive APIs and downloads all photos from a specified Google Drive folder.
# Need the API Credentials Json to be kept in folder.
# Also when you execute thsi code it will prompt to authenticate your google Drive access 2FA
#====================================================================================
#

# http://localhost:50409/
# http://localhost (for good measure)
# You can also add a range: 
# http://localhost:8080/ through http://localhost:65535/

from __future__ import print_function
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# ---------------------------------------------------------
# Google Drive Authentication
# ---------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None

    # Load token if exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid token, authenticate again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Use a fixed port that's registered in Google Cloud Console
            creds = flow.run_local_server(port=8080)
        # Save token
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


# ---------------------------------------------------------
# Get all files inside a folder (recursive)
# ---------------------------------------------------------
def list_files_recursive(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get('files', [])
    all_files = []

    for f in files:
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            # Recurse into subfolder
            all_files.extend(list_files_recursive(service, f['id']))
        else:
            all_files.append(f)

    return all_files


# ---------------------------------------------------------
# Download a single file
# ---------------------------------------------------------
def download_file(service, file_id, file_name, output_folder):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(output_folder, file_name)

    with open(file_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    print(f"✅ Downloaded: {file_path}")


# ---------------------------------------------------------
# Main function
# ---------------------------------------------------------
def download_photos_from_drive(folder_id, output_folder):
    service = authenticate()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("🔍 Scanning Google Drive folder...")

    all_files = list_files_recursive(service, folder_id)

    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic")

    for f in all_files:
        name = f['name'].lower()
        if name.endswith(image_extensions):
            download_file(service, f['id'], f['name'], output_folder)

    print("\n✅ All photos downloaded successfully!")


# ---------------------------------------------------------
# Run the script
# ---------------------------------------------------------
if __name__ == "__main__":
    
    # https://drive.google.com/drive/folders/1JPCHTmND6uZ4g6uhRGoyG0fJBGWWH0oX
    GOOGLE_FOLDER_ID = "1JPCHTmND6uZ4g6uhRGoyG0fJBGWWH0oX"
    OUTPUT_FOLDER = r"C:\Work\FMF\app\gdrive\Downloads"

    download_photos_from_drive(GOOGLE_FOLDER_ID, OUTPUT_FOLDER)
