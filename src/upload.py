import dropbox
import logging
import os
import json
from datetime import datetime, timedelta, timezone
import requests
import time

def load_config(json_file):
    with open(json_file, 'r') as f:
        config = json.load(f)
    return config

def init_dropbox_client(access_token):
    return dropbox.Dropbox(access_token, user_agent="Dropbox-Python-SDK/12.0.0")

def send_files(dbx, local_folder_path):
    for file_name in os.listdir(local_folder_path):

        if file_name == '.gitignore':
            continue

        local_file_path = os.path.join(local_folder_path, file_name)
        dropbox_file_path = os.path.join('/', file_name)


        if os.path.isfile(local_file_path):
            with open(local_file_path, 'rb') as f:
                try:
                    dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode.overwrite)
                    logger.info(f"Uploaded file: {local_file_path} to {dropbox_file_path}")

                    os.remove(local_file_path)
                    logger.info(f"Deleted local file: {local_file_path}")

                except dropbox.exceptions.ApiError as e:
                    logger.error(f"Failed to upload file: {local_file_path}, error: {e}")

def list_files(dbx, folder_path):
    files = []
    try:
        result = dbx.files_list_folder(folder_path, recursive=False)

        while True:
            files.extend(result.entries)
            if not result.has_more:
                break
            result = dbx.files_list_folder_continue(result.cursor)
    except dropbox.exceptions.ApiError as e:
        logger.error(f"Failed to list files in folder '{folder_path}', error: {e}")

    return files

def delete_old_files(dbx, files, date_time_threshold):
    for file in files:
        if isinstance(file, dropbox.files.FileMetadata) and file.client_modified < date_time_threshold:
            try:
                dbx.files_delete_v2(file.path_lower)
                logger.info(f"Deleted file: {file.path_display}")
            except dropbox.exceptions.ApiError as e:
                logger.error(f"Failed to delete file: {file.path_display}, error: {e}")

def refresh_access_token(client_id, client_secret, refresh_token):
    token_url = "https://api.dropbox.com/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    response = requests.post(token_url, headers=headers, data=payload)
    response_json = response.json()

    if response.status_code != 200:
        raise Exception(f"Error refreshing access token: {response_json}")

    return response_json["access_token"]

def upload():
    while True:
        # Load the configuration from the JSON file
        with open("cfg/dropbox.json", "r") as config_file:
            config = json.load(config_file)
    
        # Refresh the access token
        access_token = refresh_access_token(
            config["client_id"], config["client_secret"], config["refresh_token"]
        )
    
        dbx = init_dropbox_client(access_token)
    
        # Set folder paths and date/time threshold
        local_folder_path = 'data'
        current_time = datetime.now()
        date_time_threshold = current_time - timedelta(days=5)
    
        # Send files from the local folder to Dropbox and delete them locally
        send_files(dbx, local_folder_path)
    
        # Delete files older than 3 days in Dropbox
        files = list_files(dbx, '')
        delete_old_files(dbx, files, date_time_threshold)

        logging.info("Sleeping")
        time.sleep(60 * 60 * 4)  # Sleep for 4 hours

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    upload()

