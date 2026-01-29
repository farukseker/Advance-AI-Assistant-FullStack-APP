from pydantic import BaseModel


class DocumentRemoveRequest(BaseModel):
    filename: str