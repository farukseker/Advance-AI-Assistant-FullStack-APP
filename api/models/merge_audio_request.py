from pydantic import BaseModel
from typing import Union


class MergeAudioRequest(BaseModel):
    history_id: Union[str, int]
    content_s3_key: str