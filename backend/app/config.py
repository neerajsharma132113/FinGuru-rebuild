import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file, if there is one

DB_FILE = os.getenv("DB_FILE", "finguru.db")

SECRET_KEY = os.getenv("SECRET_KEY")
def parse_origins(text):
    origins = []
    for part in text.split(","):
        if part.strip() != "":
            origins.append(part.strip())
    return origins


CORS_ORIGINS = parse_origins(
    os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
)