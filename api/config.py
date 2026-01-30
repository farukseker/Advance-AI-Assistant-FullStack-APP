import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env only if it exists (local dev)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=False)

def env(key: str, default=None):
    return os.getenv(key, default)

OPENROUTER_API_KEY = env("OPENROUTER_API_KEY")
OPENROUTER_API_HOST = env("OPENROUTER_API_HOST")
STT_MODEL = env("STT_MODEL")
MONGO_URI = env("MONGO_URI")
QDRANT_URI = env("QDRANT_URI")
BASE_EMBEDDING_MODEL = env("BASE_EMBEDDING_MODEL")
DEFAULT_MODEL = env("DEFAULT_MODEL")

BUCKET_ENDPOINT_URL = env("BUCKET_ENDPOINT_URL")
BUCKET_ACCESS_KEY = env("BUCKET_ACCESS_KEY")
BUCKET_SECRET_KEY = env("BUCKET_SECRET_KEY")
BUCKET_NAME = env("BUCKET_NAME")
