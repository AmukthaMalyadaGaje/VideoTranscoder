from pymongo import MongoClient
from app.config import Config
from datetime import datetime
from app.models import Video

client = MongoClient(Config.MONGO_URI)
db = client.get_database()


def store_video_metadata(video_data: dict):
    video = Video(
        video_id=video_data["video_id"],
        status="queued",
        input_url=video_data["s3_input_url"],
        input_format=video_data["input_format"],
        output_format=video_data["target_format"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.videos.insert_one(video.dict())
    return video.dict()


def update_video_status(video_id: str, status: str, transcoded_video_url: str = ""):
    video = db.videos.find_one_and_update(
        {"video_id": video_id},
        {
            "$set": {
                "status": status,
                "transcoded_video_url": transcoded_video_url,
                "updated_at": datetime.utcnow(),
            }
        },
        return_document=True,
    )
    return video
