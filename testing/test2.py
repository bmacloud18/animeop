# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import subprocess
import isodate
import time
from openai import OpenAI

from collections import deque 

#import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

from dotenv import load_dotenv

load_dotenv()

OpenAI.api_key = os.environ.get('OPENAI_API_KEY')
yt_key = os.environ.get('YT_API_KEY')

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client = OpenAI()

yt_string = "https://www.youtube.com/watch?v="

model = "gpt-3.5-turbo"

#@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completions_with_backoff():
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you can only respond with id strings and cannot conversate"},
            {"role": "user", "content": "give me the youtube ids of 5 good japanese anime openings or endings in a comma separated list, only respond with ids and no other music"},
        ],
        temperature=.7,
        max_tokens = 100
    )
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

def get_videos():
    q = deque(completions('').choices[0].message.content.split(','))
    print(q)
    return q

def play_vid(youtube, query):
    request = youtube.search().list(
        type="video",
        maxResults=1,
        q=query,
        part='id'
    )
    response = request.execute()
    id_value = response['items'][0]['id']['videoId']
    video_url = yt_string + id_value
    print(video_url)

    req2 = youtube.videos().list(
        part='contentDetails',
        id=id_value
    )

    res2 = req2.execute()
    duration_str = res2['items'][0]['contentDetails']['duration']
    duration = isodate.parse_duration(duration_str).total_seconds() + 7

    vlc_cmd = ['vlc', video_url]
    vlc_sub = subprocess.Popen(vlc_cmd)
    time.sleep(duration)
    vlc_sub.kill()

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    # Get credentials and create an API client
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=yt_key)

    queue = get_videos()
    #play_vid(youtube, queue.pop())

    while(len(queue) > 0):
        play_vid(youtube, queue.pop())

    

if __name__ == "__main__":
    main()