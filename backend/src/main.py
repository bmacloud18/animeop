import os
import logging
from openai import OpenAI

from fastapi import FastAPI

from collections import deque 

import googleapiclient.discovery
# import googleapiclient.errors
# from google.oauth2 import service_account

from dotenv import load_dotenv
load_dotenv()

import psycopg
from psycopg.rows import dict_row
DB_URL = os.environ.get('DB_URL')

connection = psycopg.connect(
    host=os.environ.get('DB_HOST'),
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    port=os.environ.get('DB_PORT'),
    row_factory=dict_row,
    options="-c search_path=public"
)

from src.samples import samples

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

logger = logging.getLogger("animeop")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def completions(prompt, history):
    if prompt == '':
        prompt = "list 10 random great anime openings or endings"
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. you can only respond with a comma separated list. do not add duplicate items to your list. do not include items already included in this history list - ${history}"},
            {"role": "user", "content": "I am a big anime fan. I love the intro and outro videos that are famous to anime culture. List 3 anime openings and/or endings that you think I would enjoy."},
            {"role": "assistant", "content": "Naruto Opening 4, Naruto Shippuden Ending 6, Bleach Opening 1"},
            {"role": "user", "content": "list 10 more random anime openings or endings that I would enjoy."},
        ],
        temperature=.8,
        max_tokens = 100
    )

@app.on_event("startup")
async def startup_event():
    logger.debug("startup complete")

@app.get("/")
def get_home():
    """
        testurl
    """
    return ["testing"]

@app.get("/db")
def db_test():
    """
        reset db
    """
    with connection.cursor() as db:
        db.execute("SET search_path TO public")
        try:
            db.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    vid_title TEXT NOT NULL,
                    vid_url TEXT NOT NULL
                );
            """)
            db.execute("""
                DELETE FROM videos;
            """)
            db.execute("""
                INSERT INTO videos (vid_title, vid_url) VALUES 
                    ('Fairy Tail Opening 1', 'https://www.youtube.com/watch?v=9jvVBVcZ0-Y'), 
                    ('Dragon Ball Z Opening', 'https://www.youtube.com/watch?v=R4vjJrGeh1c'),
                    ('One Piece Opening 20', 'https://www.youtube.com/watch?v=Oo52vQyAR6w'),
                    ('Demon Slayer Opening 1', 'https://www.youtube.com/watch?v=YkJvHe3KK2c'),
                    ('Sword Art Online Opening 1', 'https://www.youtube.com/watch?v=1oOBjyOKu2o'),
                    ('Tokyo Ghoul Opening 1', 'https://www.youtube.com/watch?v=7aMOurgDB-o'),
                    ('Death Note Opening 1', 'https://www.youtube.com/watch?v=kNyR46eHDxE'),
                    ('My Hero Academia Opening 1', 'https://www.youtube.com/watch?v=yu0HjPzFYnY'),
                    ('Fullmetal Alchemist: Brotherhood Opening 1', 'https://www.youtube.com/watch?v=elyXcwunIYA'),
                    ('Attack on Titan Opening 1', 'https://www.youtube.com/watch?v=8OkpRK2_gVs');
            """)
            connection.commit()
            db.execute('SELECT * FROM videos')
            return (['db test:', DB_URL] + db.fetchall())
        except Exception as e:
            logger.debug('error accessing db')
            return 'error occurred: ' + str(e)

@app.get("/videos")
def get_videos(query: str, history: str):
    """
        if needed return samples to save tokens and continue testing (line 81)
    """
    raw_completions = deque(completions(query, history).choices[0].message.content.split(','))
    q = deque([[]])
    while len(raw_completions) > 0:
        yt_query = raw_completions.pop().strip()
        ret_url = ''
        logger.debug('query: ' + yt_query)
        with connection.cursor() as db:
            db.execute("SET search_path TO public")
            try:
                db.execute('SELECT * FROM videos WHERE vid_title=%s', [yt_query])
                ret_obj = db.fetchall()
                if (ret_obj):
                    ret_url = ret_obj[0]['vid_url']
                logger.debug('url: ' + ret_url)
            except Exception as e:
                logger.debug(f"video not found")
        if len(ret_url) < 2:
            request = youtube.search().list(
                type="video",
                maxResults=1,
                q=yt_query,
                part='id'
            )
            try:
                response = request.execute()
            except Exception as e:
                logger.debug('out of yt tokens')
                return samples
            id_value = response['items'][0]['id']['videoId']
            video_url = yt_string + id_value
            with connection.cursor() as db:
                db.execute('INSERT INTO videos (vid_title, vid_url) VALUES (%s, %s)', [yt_query, video_url])
                connection.commit()
        else:
            logger.debug('retrieved a cached url')
            video_url = ret_url
        q.append([video_url, yt_query])
    return [*q]
#     
    
    