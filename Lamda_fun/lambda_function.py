import json
import boto3
import requests
import subprocess
import os
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import logging
import tempfile

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3_client = boto3.client("s3")
sqs_client = boto3.client("sqs")

# Backend URL for status update (adjust as needed)
BACKEND_API_URL = "http://127.0.0.1:8000/video_status"


def get_bitrate_for_quality(quality: str) -> str:
    """
    Returns an appropriate video bitrate based on the desired quality.
    Expects quality in the form '360p', '480p', '720p', etc.
    """
    try:
        height = int("".join(filter(str.isdigit, quality)))
        if height <= 360:
            return "800k"
        elif height <= 480:
            return "1200k"
        elif height <= 720:
            return "2500k"
        elif height <= 1080:
            return "5000k"
        else:
            return "8000k"
    except ValueError:
        logger.warning(
            f"Invalid quality value provided: {quality}. Skipping bitrate adjustment."
        )
        return None


def get_quality_filter(quality: str) -> list:
    """
    Returns the FFmpeg video filter parameters for scaling the video
    to the desired quality. For example, if quality is '360p', the filter will be:
    ['-vf', 'scale=-2:360'].
    """
    if quality:
        try:
            height = int("".join(filter(str.isdigit, quality)))
            return ["-vf", f"scale=-2:{height}"]
        except ValueError:
            logger.warning(
                f"Invalid quality value provided: {quality}. Skipping quality adjustment."
            )
            return []
    return []


def get_ffmpeg_params(
    input_format: str, target_format: str, quality: str = None
) -> tuple:
    """
    Returns the FFmpeg parameters:
      - video codec
      - audio codec
      - extra parameters (including bitrate adjustments)
      - container flag (if needed)
    based on the desired output format and quality.
    """
    target_format = target_format.lower()
    input_format = input_format.lower()

    container_flag = []

    if target_format == "mp4":
        video_codec = "libx264"
        audio_codec = "aac"
        extra_params = ["-movflags", "faststart"]
    elif target_format == "mkv":
        video_codec = "libx264"
        audio_codec = "aac"
        extra_params = []
    elif target_format == "mov":
        video_codec = "prores_ks"  # ProRes is common for MOV files
        audio_codec = "pcm_s16le"
        container_flag = ["-f", "mov"]
        extra_params = []
    elif target_format == "avi":
        video_codec = "mpeg4"
        audio_codec = "mp3"
        extra_params = []
    else:
        video_codec = "libx264"
        audio_codec = "aac"
        extra_params = []

    # If a quality is specified, adjust the bitrate accordingly.
    if quality:
        bitrate = get_bitrate_for_quality(quality)
        if bitrate:
            extra_params.extend(["-b:v", bitrate])
    else:
        # Optionally adjust bitrate based on input format (if quality is not explicitly provided)
        if input_format == "hevc" and target_format in ["mp4", "mkv"]:
            extra_params.extend(["-b:v", "1500k"])

    return video_codec, audio_codec, extra_params, container_flag


def lambda_handler(event, context):
    """
    AWS Lambda handler to process SQS messages for video transcoding.
    Each message is expected to contain:
      - video_id: Unique identifier for the video.
      - s3_input_url: The S3 URL of the uploaded video.
      - input_format: Format/extension of the input video.
      - output_format: Desired output video format.
      - quality: Desired quality (e.g., '360p', '480p', etc.)
    """
    for record in event["Records"]:
        # Initialize file path variables
        tmp_file_path = None
        output_file_path = None

        try:
            # Parse the incoming SQS message
            message_body = json.loads(record["body"])
            video_id = message_body["video_id"]
            s3_input_url = message_body["s3_input_url"]
            input_format = message_body["input_format"]
            target_format = message_body["output_format"]
            quality = message_body.get("video_quality")  # e.g., "360p", "480p", etc.

            logger.info(
                f"Received message for video: {video_id} | Input: {input_format} | "
                f"Target: {target_format} | Quality: {quality}"
            )

            # Update video status to "in-progress"
            update_video_status(video_id, "in-progress")

            # Parse bucket and key from the S3 URL
            parsed_url = urlparse(s3_input_url)
            s3_bucket = parsed_url.netloc.split(".")[0]
            s3_key = parsed_url.path.lstrip("/")

            # Download the video from S3 to a temporary file
            with NamedTemporaryFile(
                delete=False, suffix=f".{input_format}"
            ) as tmp_file:
                tmp_file_path = tmp_file.name
            s3_client.download_file(s3_bucket, s3_key, tmp_file_path)
            logger.info(f"Downloaded video to: {tmp_file_path}")

            # Determine output file path (including quality in the name)
            file_suffix = f"_{quality}" if quality else ""
            output_file_name = f"transcoded_video{file_suffix}.{target_format}"
            output_file_path = os.path.join(tempfile.gettempdir(), output_file_name)

            # Get FFmpeg parameters and quality filter options
            video_codec, audio_codec, extra_params, container_flag = get_ffmpeg_params(
                input_format, target_format, quality
            )
            quality_filter = get_quality_filter(quality)

            # Specify the path to your FFmpeg binary (update as needed)
            ffmpeg_path = r"C:\Users\devad\OneDrive\Desktop\Lamda_fun\ffmpeg\ffmpeg\bin\ffmpeg.exe"

            # Build the FFmpeg command
            transcoding_command = [
                ffmpeg_path,
                "-i",
                tmp_file_path,
                "-c:v",
                video_codec,
            ]
            if quality_filter:
                transcoding_command.extend(quality_filter)
            transcoding_command.extend(["-c:a", audio_codec])
            transcoding_command.extend(extra_params)
            transcoding_command.extend(container_flag)
            transcoding_command.append(output_file_path)

            logger.info(
                f"Starting transcoding with command: {' '.join(transcoding_command)}"
            )
            subprocess.run(transcoding_command, check=True)
            logger.info("Transcoding completed successfully.")

            # Upload the transcoded video back to S3
            transcoded_key = (
                f"transcoded/{video_id}_transcoded{file_suffix}.{target_format}"
            )
            s3_client.upload_file(output_file_path, s3_bucket, transcoded_key)
            logger.info(
                f"Uploaded transcoded video to: s3://{s3_bucket}/{transcoded_key}"
            )

            # Generate the S3 URL for the transcoded video
            transcoded_video_url = (
                f"https://{s3_bucket}.s3.amazonaws.com/{transcoded_key}"
            )

            # Notify the backend that processing is completed
            update_video_status(video_id, "completed", transcoded_video_url)

        except subprocess.CalledProcessError as e:
            logger.error(f"Transcoding failed for video {video_id}: {e}")
            update_video_status(video_id, "failed", None)
        except Exception as e:
            logger.error(f"Unexpected error for video {video_id}: {e}")
            update_video_status(video_id, "failed", None)
        finally:
            # Clean up temporary files if they exist
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            if output_file_path and os.path.exists(output_file_path):
                os.remove(output_file_path)

    return {"statusCode": 200, "body": json.dumps("Video transcoding completed")}


def update_video_status(video_id: str, status: str, transcoded_video_url: str = None):
    """
    Sends an update to the backend API to change the video status.
    """
    url = f"{BACKEND_API_URL}/{video_id}"
    params = {"status": status}
    if transcoded_video_url:
        params["transcoded_video_url"] = transcoded_video_url

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logger.info(f"Updated video {video_id} status to '{status}' successfully.")
        else:
            logger.error(
                f"Failed to update status for video {video_id}: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating video {video_id} status: {e}")
