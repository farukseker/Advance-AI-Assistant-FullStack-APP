from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel
from config import DEFAULT_MODEL


class CreateChatRequest(BaseModel):
    message: Optional[str] = "Message"


class MessageRequest(BaseModel):
    question: str
    filename: Optional[UploadFile] = None
    model:  Optional[str] = DEFAULT_MODEL
    custom_prompt: Optional[str] = None