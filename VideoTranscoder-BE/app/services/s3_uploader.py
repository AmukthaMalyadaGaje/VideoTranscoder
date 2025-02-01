import boto3
from app.config import Config

s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION,
)


def upload_video_to_s3(file_path: str, file_name: str):
    try:
        s3_client.upload_file(file_path, Config.S3_BUCKET_NAME, file_name)
        file_url = f"https://{Config.S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
        return file_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
