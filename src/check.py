import os
import sys
import json
import time
import yt_dlp
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

LAST_VIDEO_FILE = "last_video_id.txt"


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


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
        print(f"An error occurred: {e}")
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


def save_last_video_id(video_id):
    with open(LAST_VIDEO_FILE, "w") as f:
        f.write(video_id)

def load_last_video_id():
    if os.path.exists(LAST_VIDEO_FILE):
        with open(LAST_VIDEO_FILE, "r") as f:
            return f.read().strip()
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Usage: python download_latest_video.py <api_key> <channel_id>")
        sys.exit(1)

    api_key = sys.argv[1]
    channel_id = sys.argv[2]
    last_video_id = load_last_video_id()

    while True:
        video_id = get_latest_video(api_key, channel_id)

        if video_id and video_id != last_video_id:
            logging.info(f"Downloading {video_id}")
            download_video_as_mp3(video_id)
            save_last_video_id(video_id)
            last_video_id = video_id
        else:
            logging.info("No new videos or couldn't find the latest video.")

        logging.info(f"Sleeping...")
        time.sleep(60 * 60 * 4)  # Sleep for 4 hour
