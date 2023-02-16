from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

# Get tokens from .env file stored in the same directory as this file
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')


def get_mp3_by_title(title):
    with build('youtube', 'v3', developerKey=YOUTUBE_API_KEY) as service:
        
        request = service.search().list(
            part='snippet',
            type='video',
            q=title,
            maxResults=1
        )
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        video_title = response['items'][0]['snippet']['title']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        return video_url, video_title
