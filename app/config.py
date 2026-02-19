import os

ADS_API_BASE_URL = os.getenv("ADS_API_BASE_URL", "http://51.250.71.134:8000")

APP_DB_DSN = os.getenv("APP_DB_DSN", "postgresql+psycopg2://app:app@localhost:5433/app")

QDRANT_URL = os.getenv("QDRANT_URL", "http://51.250.71.134:6333")

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "ads")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Коллекции Qdrant
QDRANT_TEXT_COLLECTION = os.getenv("QDRANT_TEXT_COLLECTION", "ads_text")
QDRANT_IMAGE_COLLECTION = os.getenv("QDRANT_IMAGE_COLLECTION", "ads_image")

# base parse
NEW_LINK = "https://youla.ru/moskva/auto?attributes[term_of_placement][from]=-1%20day&attributes[term_of_placement][to]=now&attributes[sort_field]=date_published"