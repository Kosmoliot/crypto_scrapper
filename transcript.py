import os
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime


load_dotenv()

# Define API key and channel ID
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is not set.")

CHANNEL_ID = "UCHop-jpf-huVT1IYw79ymPw"

def transcript(video_id):
    """Retrieve transcript for a given video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        video_transc = []
        for item in transcript_list:
            video_transc.append(item['text'])
        return ' '.join(video_transc)
    except Exception as e:
        print(f"Failed to retrieve transcript for video {video_id}: {e}")
        return None

class Chico_video():
    """Class to store video parameters."""
    def __init__(self, video_id, video_date, video_title, video_coins) -> None:
        self.video_id = video_id
        self.video_date = video_date
        self.video_title = video_title
        self.video_coins = video_coins


def get_video_ids():
    """Retrieve video IDs, date, title, and coins list."""
    try:
        # Define the YouTube API service. Achieving resource cleanup by using "with" statement
        with build("youtube", "v3", developerKey=API_KEY) as youtube:

            videos =[]
            
            # Define the time period
            start_date = datetime(2024, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')
            end_date = datetime(2024, 12, 31).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            next_page_token = None
            
            # Fetch initial page of results
            while True:
                # Retrieve videos from the channel with pagination
                request = youtube.search().list(
                    part="snippet",
                    channelId=CHANNEL_ID,
                    publishedAfter = start_date,
                    publishedBefore = end_date,
                    maxResults=10,  # Adjust the number of results as needed
                    type="video",   # Necessary for using videoDuration parameter
                    videoDuration="medium" , # Video length from 4 to 20 minutes
                )
                response = request.execute()
                
                # Extract video IDs, date, title, and coim list fro, the response
                for item in response.get("item", []):
                    if item["id"]["kind"] == "youtube#video":
                        video_id = item["id"]["videoId"]
                        published_date = item["snippet"]["publishedAt"]
                        video_title = item["snippet"]["title"]
                        video_coins = transcript_filter(transcript(video_id))
                        videos.append(Chico_video(video_id, published_date, video_title, video_coins))
                
                return videos

    except Exception as e:
        print(f"Failed to retrieve a list of videos: {e}")
        return []


def transcript_filter(text):
    """"Filter transcript using OpenAI."""
    try:
        client = OpenAI()

        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """You are analyzing a cryptocurrency youtube content creator.
            Your goal is to identify all the crypto coins or protocols that youtube content creator 
            regards as profitable or 'bullish'. Please put all of these crypto coin's or protocol's 
            names in a single python list format, i.e. all names in single quotes inside square brackets, 
            separated by comma and no other text"""},
            {"role": "user", "content": text}
        ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Failed to filter transcript: {e}")

# if __name__ == "__main__":
#     get_video_ids()
    
print(get_video_ids())