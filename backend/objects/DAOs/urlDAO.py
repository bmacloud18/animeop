import os
import logging
import random

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
