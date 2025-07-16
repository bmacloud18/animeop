import os
from jose import jwt
from datetime import datetime, timedelta, timezone

from openai import OpenAI

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


from dotenv import load_dotenv
load_dotenv()

TOKEN_NAME = os.environ.get('TOKEN_NAME')
API_SECRET = os.environ.get('API_SECRET')
ALGORITHM = "HS256"
EXP_TIME = 900 # < 15 minutes left


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
        get_token()
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
    return True