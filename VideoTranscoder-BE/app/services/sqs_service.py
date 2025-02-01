import boto3
from app.config import Config

sqs_client = boto3.client(
    "sqs",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_REGION,
)


def send_message_to_queue(
    video_id: str,
    s3_input_url: str,
    input_format: str,
    output_format: str,
    video_quality: str,
):
    message_body = {
        "video_id": video_id,
        "s3_input_url": s3_input_url,
        "input_format": input_format,
        "output_format": output_format,
        "video_quality": video_quality,
    }

    # The MessageGroupId is required for FIFO queues to ensure ordered processing
    # You can use the video_id or any other logic that groups the messages
    message_group_id = video_id  # or any other unique string to group the messages

    response = sqs_client.send_message(
        QueueUrl=Config.SQS_QUEUE_URL,
        MessageBody=str(message_body),
        MessageGroupId=message_group_id,  # Add this parameter for FIFO queues
    )
    return response
