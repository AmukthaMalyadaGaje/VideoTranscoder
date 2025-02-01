from pydantic import BaseModel
from datetime import datetime


class Video(BaseModel):
    video_id: str
    status: str  # e.g., "queued", "in-progress", "completed"
    input_url: str
    transcoded_video_url: str = None
    input_format: str
    output_format: str
    created_at: datetime
    updated_at: datetime
