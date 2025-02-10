import os
import subprocess
import isodate
import time
from openai import OpenAI
import json

from fastapi import FastAPI, Depends, Response
from typing import Annotated, Any, Optional, List, Dict

from collections import deque 

import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

from dotenv import load_dotenv

load_dotenv()

OpenAI.api_key = os.environ.get('OPENAI_API_KEY')
yt_key = os.environ.get('YT_API_KEY')

api_service_name = "youtube"
api_version = "v3"

# Get credentials and create an API client
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
            {"role": "system", "content": "You are a helpful assistant. you can only respond with a comma separated list"},
            {"role": "user", "content": "list the top 3 best anime openings"},
            {"role": "assistant", "content": "Naruto Opening 4, Naruto Opening 6, Bleach Opening 1"},
            {"role": "user", "content": "list 10 random great anime openings or endings"},
        ],
        temperature=.4,
        max_tokens = 100
    )

@app.get("/videos")
def get_videos(response: Response, query: str):
    """
    """
    raw_completions = deque(completions(query).choices[0].message.content.split(','))
    q = deque([])
    while len(raw_completions) > 0:
        request = youtube.search().list(
            type="video",
            maxResults=1,
            q=query,
            part='id'
        )
        response = request.execute()
        id_value = response['items'][0]['id']['videoId']
        video_url = yt_string + id_value
        q.append(video_url)

    return q
    