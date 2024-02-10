# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import subprocess
import backoff
import openai
#import isodate
from openai import OpenAI

#import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import service_account

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
client = OpenAI()

model = "gpt-3.5-turbo"

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completions_with_backoff():
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you can only respond with id strings and cannot conversate"},
            {"role": "user", "content": "give me the youtube ids of 5 good anime openings or endings in a comma separated list, only respond with ids"},
            {"role": "assistant", "content": "VzqYWTgPFpA,CAuDWXsMquk,5uq34TeWEdQ,smanD_sL1w8,M-zvzz8MxFg"},
            {"role": "user", "content": "give me 5 more youtube ids of good anime openings or endings in a comma separated list"},
        ],
        temperature=0,
        max_tokens = 50
    )
def completions():
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you can only respond with id strings and cannot conversate"},
            {"role": "user", "content": "give me the youtube ids of 5 good anime openings or endings in a comma separated list, only respond with ids"},
            {"role": "assistant", "content": "VzqYWTgPFpA,CAuDWXsMquk,5uq34TeWEdQ,smanD_sL1w8,M-zvzz8MxFg"},
            {"role": "user", "content": "give me 5 more youtube ids of good anime openings or endings in a comma separated list"},
        ],
        temperature=0,
        max_tokens = 50
    )

def extract_video_url(embed_html):
    # Extract the video URL from the embed HTML code
    start_index = embed_html.find('src="') + len('src="')
    end_index = embed_html.find('" fr')
    video_url = embed_html[start_index:end_index]
    return "https:" + video_url

def get_video_ids():
    response = completions()

    print(response.choices[0].message.content)
    return response.choices[0].message.content



def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.environ.get('CS_FILE')

    # Get credentials and create an API client
    credentials = service_account.Credentials.from_service_account_file(
        client_secrets_file, scopes=scopes)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    video_ids = get_video_ids()
    """request = youtube.videos().list(
        part="contentDetails, player",
        ids=video_ids
    )
    response = request.execute()

    embed_html = response['items'][0]['player']['embedHtml']
    video_url = extract_video_url(embed_html)
    #duration_str = response['items'][0]['contentDetails']['duration']
    #duration = isodate.parse_duration(duration_str)

    vlc_cmd = ['vlc', video_url]
    #subprocess.Popen(vlc_cmd)
    print(response)
    """

if __name__ == "__main__":
    main()