from pydantic import BaseModel


class MergeAudioRequest(BaseModel):
    history_id: str
    content_s3_key: str