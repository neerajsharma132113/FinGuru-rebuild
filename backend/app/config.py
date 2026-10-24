import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file, if there is one

DB_FILE = os.getenv("DB_FILE", "finguru.db")