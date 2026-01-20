from dotenv import dotenv_values

config = dotenv_values(".env")

OPENROUTER_API_KEY = config.get("OPENROUTER_API_KEY")
OPENROUTER_API_HOST = config.get("OPENROUTER_API_HOST")
STT_MODEL = config.get("STT_MODEL")
MONGO_URI = config.get('MONGO_URI')
QDRANT_URI = config.get('QDRANT_URI')
BASE_EMBEDDING_MODEL = config.get('BASE_EMBEDDING_MODEL')
DEFAULT_MODEL = config.get('DEFAULT_MODEL')