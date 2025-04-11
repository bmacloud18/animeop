import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()  # load from .env

connection = psycopg.connect(os.getenv("DB_URL"), row_factory=dict_row)