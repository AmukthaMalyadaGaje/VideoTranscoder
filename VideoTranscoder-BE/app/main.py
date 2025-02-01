import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query, Path
from app.services.s3_uploader import upload_video_to_s3
from app.services.sqs_service import send_message_to_queue
from app.services.mongo_service import store_video_metadata, update_video_status
from app.models import Video

# cors policy use here
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_video/")
async def upload_video(
    file: UploadFile = File(...),
    output_format: str = Form(...),
    video_quality: str = Form(...),
):
    print("Received a request to upload a video")

    # Generate a unique video_id and create a unique file name for S3
    video_id = str(uuid.uuid4())
    file_name = f"{video_id}_{file.filename}"

    # Extract the input file type from the original file name (e.g. 'mp4', 'mkv')
    _, file_extension = os.path.splitext(file.filename)
    input_format = file_extension.lower().lstrip(".")  # e.g. 'mp4'

    tmp_file_path = None

    try:
        # Use a temporary file to store the uploaded file content
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(await file.read())
            tmp_file_path = tmp_file.name

        # Upload the file to S3
        s3_input_url = upload_video_to_s3(tmp_file_path, file_name)
        print(f"Video uploaded to S3 successfully: {s3_input_url}")
        if not s3_input_url:
            raise HTTPException(status_code=500, detail="Failed to upload video to S3")

        # Store video metadata in MongoDB (you might consider including formats here as well)
        video_data = {
            "video_id": video_id,
            "s3_input_url": s3_input_url,
            "input_format": input_format,
            "target_format": output_format,
            "video_quality": video_quality,
        }
        store_video_metadata(video_data)

        # Send the transcoding job to SQS with input and output format details
        res = send_message_to_queue(
            video_id, s3_input_url, input_format, output_format, video_quality
        )
        print("Response from SQS:", res)
        print(f"Transcoding job sent to SQS for video {video_id}")

        return {"message": "Video uploaded successfully", "video_id": video_id}

    finally:
        # Clean up the temporary file after use
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)


@app.get("/video_status/{video_id}")
async def get_video_status(
    video_id: str = Path(..., title="Video ID"),
    status: str = Query("in-progress"),
    transcoded_video_url: str = Query(""),
):
    # Update the status to "in-progress", "completed", or "failed"
    video = update_video_status(video_id, status, transcoded_video_url)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "video_id": video_id,
        "status": status,
        "transcoded_video_url": transcoded_video_url,
    }
