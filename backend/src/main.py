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

from samples import samples

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

LEVEL = logging.DEBUG

logger = logging.getLogger("animeop")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
handler.setLevel(LEVEL)

logger.addHandler(handler)
logger.propagate = False

NUM_RES = 10

def completions(prompt, history):
    if prompt == '':
        prompt = "list 10 random great anime openings or endings"
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. you can only respond with a comma separated list. do not add duplicate items to your list. do not include items already included in this history list - {history}"},
            {"role": "user", "content": "I am a big anime fan. I love the intro and outro videos that are famous to anime culture. List 3 anime openings and/or endings that you think I would enjoy."},
            {"role": "assistant", "content": "Naruto Opening 4, Naruto Shippuden Ending 6, Bleach Opening 1"},
            {"role": "user", "content": f"list {NUM_RES} more random anime openings or endings that I would enjoy."},
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
    # logger.debug(connection)
    try:
        with connection.cursor() as db:
                db.execute("SET search_path TO public")
                try:
                    db.execute('SELECT * FROM videos')
                    ret_obj = db.fetchall()
                    pr = []
                    if (ret_obj):
                        for i in ret_obj:
                            ret_url = i['vid_title']
                            pr.append(ret_url)
                    logger.debug(f'returning {len(pr)} items')
                except Exception as e:
                    logger.error('error: %s', e)
    except Exception as e:
        logger.error(f'error connecting to db: {e}')
    return pr

@app.get("/db")
def db_test():
    """
        reset db
    """
    with connection.cursor() as db:
        try:
            db.execute("SET search_path TO public")
            db.execute("DROP TABLE videos")
            connection.commit()

            db.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    vid_url TEXT PRIMARY KEY NOT NULL,
                    vid_title TEXT NOT NULL
                );
            """)
            db.execute("""
                DELETE FROM videos;
            """)
            db.execute("""
                INSERT INTO videos (vid_url, vid_title) VALUES 
                    ('https://www.youtube.com/watch?v=8OkpRK2_gVs', 'Attack on Titan Opening 1'),
                    ('https://www.youtube.com/watch?v=elyXcwunIYA', 'Fullmetal Alchemist: Brotherhood Opening 1'),
                    ('https://www.youtube.com/watch?v=yu0HjPzFYnY', 'My Hero Academia Opening 1'),
                    ('https://www.youtube.com/watch?v=kNyR46eHDxE', 'Death Note Opening 1'),
                    ('https://www.youtube.com/watch?v=7aMOurgDB-o', 'Tokyo Ghoul Opening 1'),
                    ('https://www.youtube.com/watch?v=1oOBjyOKu2o', 'Sword Art Online Opening 1'),
                    ('https://www.youtube.com/watch?v=YkJvHe3KK2c', 'Demon Slayer Opening 1'),
                    ('https://www.youtube.com/watch?v=Oo52vQyAR6w', 'One Piece Opening 20'),
                    ('https://www.youtube.com/watch?v=R4vjJrGeh1c', 'Dragon Ball Z Opening'),
                    ('https://www.youtube.com/watch?v=9jvVBVcZ0-Y', 'Fairy Tail Opening 1');
            """)
            connection.commit()
            db.execute('SELECT * FROM videos')
            return (['db test:', DB_URL] + db.fetchall())
        except Exception as e:
            logger.error('error accessing db')
            return 'error occurred: %s', e

@app.get("/videos")
def get_videos(query: str, history: str):
    """
        if needed return samples to save tokens and continue testing (line 81)
    """
    raw_completions = deque(completions(query, history).choices[0].message.content.split(','))
    logger.debug(raw_completions)
    q = deque([[]])
    while len(raw_completions) > 0:
        n = NUM_RES - len(raw_completions)
        logger.debug("%s", n)
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
                logger.error('out of yt tokens')
                logger.debug('returning samples')
                logger.debug(samples)
                return samples
            id_value = response['items'][0]['id']['videoId']
            video_url = yt_string + id_value
            with connection.cursor() as db:
                try:
                    db.execute('INSERT INTO videos (vid_url, vid_title) VALUES (%s, %s)', [video_url, yt_query])
                    connection.commit()
                    logger.debug('video added')
                except Exception as e:
                    logger.error('unable to add video: %s', e)
        else:
            logger.debug('retrieved a cached url')
            video_url = ret_url
        q.append([video_url, yt_query])
    return [*q]
#     
    
    