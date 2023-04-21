import upload as up

import os
import sys
import json
import time
import yt_dlp
import logging
import threading
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(threadName)s] %(levelname)s: %(message)s')


def get_latest_video(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        response = youtube.search().list(
            channelId=channel_id,
            part='id',
            order='date',
            maxResults=1,
            type='video'
        ).execute()

        video_id = response['items'][0]['id']['videoId']
        return video_id

    except HttpError as e:
        logging.error(f"An error occurred: {e}")
        return None

def download_video_as_mp3(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'data/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': '/usr/bin/ffmpeg',
        'ffprobe_location': '/usr/bin/ffprobe',

    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'http://www.youtube.com/watch?v={video_id}'])

def last_video_filename(channel_id):
    return f"cfg/last_video_id_{channel_id}.txt"

def save_last_video_id(channel_id, video_id):
    with open(last_video_filename(channel_id), "w") as f:
        f.write(video_id)

def load_last_video_id(channel_id):
    last_video_file = last_video_filename(channel_id)
    if os.path.exists(last_video_file):
        with open(last_video_file, "r") as f:
            return f.read().strip()
    return None

def load_config():
    with open("cfg/api_key-channel_id.json", "r") as f:
        config = json.load(f)
    return config


def monitor_channel(api_key, channel_id):
    # Set the current thread's name to the channel ID for easier log identification
    threading.current_thread().name = channel_id
    
    last_video_id = load_last_video_id(channel_id)

    while True:
        video_id = get_latest_video(api_key, channel_id)

        if video_id and video_id != last_video_id:
            logging.info(f"Downloading video with ID: {video_id}")
            download_video_as_mp3(video_id)
            save_last_video_id(channel_id, video_id)
            last_video_id = video_id
        else:
            logging.info("No new videos or couldn't find the latest video.")

        up.upload()

        logging.info("Sleeping")
        time.sleep(60 * 60)  # Sleep for 1 hour (3600 seconds)

if __name__ == "__main__":
    config = load_config()
    api_key = config['api_key']
    channel_ids = config['channel_ids']

    threads = []
    for channel_id in channel_ids:
        thread = threading.Thread(target=monitor_channel, args=(api_key, channel_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
