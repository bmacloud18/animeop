import os
import logging
import random

from openai import OpenAI

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware



from collections import deque 

import googleapiclient.discovery
# import googleapiclient.errors
# from google.oauth2 import service_account
from jose import jwt
from datetime import datetime, timedelta, timezone

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

# src.samples needs to be samples for local runs
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

# setup FastAPI backend application, allowing CORS requests from domain
app = FastAPI()
origins = [
    "https://theabbottsonline.com",
    "https://theabbottsonline.com:3000",
    "https://www.theabbottsonline.com",
    "https://www.theabbottsonline.com:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all (use with care)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEVEL = logging.DEBUG

logger = logging.getLogger("animeop")
logger.setLevel(LEVEL)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
handler.setLevel(LEVEL)

logger.addHandler(handler)
logger.propagate = False

NUM_RES = 10

TOKEN_NAME = os.environ.get('TOKEN_NAME')
API_SECRET = os.environ.get('API_SECRET')
ALGORITHM = "HS256"

EXP_TIME = 900 # < 15 minutes left


# have chat gpt return a formatted list of popular anime openings and endings, change number of results with NUM_RES
# avoids repeating values used in history list provided by api query params
# in the future may add more customization to prompt parameter - time period, genre, etc.
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

# debug
@app.on_event("startup")
async def startup_event():
    logger.debug("startup complete")

# test url, retrieves all cached videos
@app.get("/")
def get_home():
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

@app.post("/")
def get_token():
    payload = {
        "sub": "frontend-client",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
        "scope": "frontend only"
    }
    token = jwt.encode(payload, API_SECRET, algorithm=ALGORITHM)

    response = JSONResponse(content={"message": "Token set in cookie"})
    response.set_cookie(
        key=TOKEN_NAME,
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    return response
    
def verify_token(request: Request, response: JSONResponse = None):
    token = request.cookies.get(TOKEN_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="oops! unauthorized")

    try:
        payload = jwt.decode(token, API_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="unauthorized access")

    # renew token if expiring soon
    exp = datetime.fromtimestamp(payload["exp"])
    exp = exp.replace(tzinfo=timezone.utc)
    if (exp - datetime.now(timezone.utc)).total_seconds() < EXP_TIME:
        new_payload = {
            "sub": payload["sub"],
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "scope": "frontend only"
        }
        new_token = jwt.encode(new_payload, API_SECRET, algorithm=ALGORITHM)

        
        if response:
            response.set_cookie(
            key=TOKEN_NAME,
            value=new_token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )

    # logger.debug(payload)
    return payload

# resets database by dropping and recreating videos table with some sample values
@app.put("/db")
def db_test(request: Request):
    verify_token(request)
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

# main endpoint, retrieves a list of videos of NUM_RES length using chatgpt and youtube api with some url caching
# history parameter is a list of titles that chatgpt should omit from its next batch of results to avoid repeating videos in a short time period
# query parameter will be used in the future for time period, genre, etc.
@app.get("/videos")
def get_videos(request: Request, response: JSONResponse, query: str, history: str):
    q = deque([[]])
    verify_token(request, response)
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
            yt_request = youtube.search().list(
                type="video",
                maxResults=1,
                q=yt_query,
                part='id'
            )
            try:
                yt_response = yt_request.execute()
                id_value = yt_response['items'][0]['id']['videoId']
                video_url = yt_string + id_value
                with connection.cursor() as db:
                    try:
                        db.execute('INSERT INTO videos (vid_url, vid_title) VALUES (%s, %s) ON CONFLICT (vid_url) DO NOTHING', [video_url, yt_query])
                        connection.commit()
                        logger.debug('video added')
                    except Exception as e:
                        logger.error('unable to add video: %s', e)
            except Exception as e:
                x = random.randint(0, 9)
                video_url = samples[x][0]
                logger.error('out of yt tokens: %s', e)
                # logger.debug('returning samples')
                # logger.debug(samples)
                # return samples
        else:
            logger.debug('retrieved a cached url')
            video_url = ret_url
        q.append([video_url, yt_query])
    return [*q]