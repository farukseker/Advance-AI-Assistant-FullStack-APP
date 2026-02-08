from dotenv import dotenv_values

config = dotenv_values("../.env")

OPENROUTER_API_KEY = config.get("OPENROUTER_API_KEY")
OPENROUTER_API_HOST = config.get("OPENROUTER_API_HOST")
STT_MODEL = config.get("STT_MODEL")
MONGO_URI = config.get('MONGO_URI')
QDRANT_URI = config.get('QDRANT_URI')
BASE_EMBEDDING_MODEL = config.get('BASE_EMBEDDING_MODEL')
DEFAULT_MODEL = config.get('DEFAULT_MODEL')
BUCKET_ENDPOINT_URL=config.get('BUCKET_ENDPOINT_URL')
BUCKET_ACCESS_KEY=config.get('BUCKET_ACCESS_KEY')
BUCKET_SECRET_KEY=config.get('BUCKET_SECRET_KEY')
BUCKET_NAME=config.get('BUCKET_NAME')