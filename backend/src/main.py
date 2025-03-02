import os
# import subprocess
# import isodate
# import time
from openai import OpenAI

from fastapi import FastAPI

from collections import deque 

import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

from dotenv import load_dotenv

from src.samples import samples

load_dotenv()

OpenAI.api_key = os.environ.get('OPENAI_API_KEY')
yt_key = os.environ.get('YT_API_KEY')

api_service_name = "youtube"
api_version = "v3"

# Get credentials and create an API client for yt
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=yt_key)

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client = OpenAI()

yt_string = "https://www.youtube.com/watch?v="

model = "gpt-3.5-turbo"

app = FastAPI()

def completions(prompt):
    if prompt == '':
        prompt = "list 10 random great anime openings or endings"
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you can only respond with a comma separated list. do not add duplicate items to your list. do not reuse answers unless prompted to discard history."},
            {"role": "user", "content": "I am a big anime fan. I love the intro and outro videos that are famous to anime culture. List 3 anime openings and/or endings that you think I would enjoy."},
            {"role": "assistant", "content": "Naruto Opening 4, Naruto Shippuden Ending 6, Bleach Opening 1"},
            {"role": "user", "content": "list 10 more random anime openings or endings that I would enjoy."},
        ],
        temperature=.4,
        max_tokens = 100
    )

@app.get("/")
def get_home():
    """
        testurl
    """
    return ["testing"]

@app.get("/videos")
def get_videos(query: str):
    """
        if needed return samples to save tokens and continue testing
    """
    raw_completions = deque(completions(query).choices[0].message.content.split(','))
    q = deque([[]])
    while len(raw_completions) > 0:
        yt_query = raw_completions.pop()
        request = youtube.search().list(
            type="video",
            maxResults=1,
            q=yt_query,
            part='id'
        )
        try:
            response = request.execute()
        except Exception as e:
            print('out of yt tokens')
            return samples
        id_value = response['items'][0]['id']['videoId']
        video_url = yt_string + id_value
        q.append([video_url, yt_query])
    return [*q]
#     
    
    