from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
    MONGO_URI = os.getenv("MONGO_URI")
