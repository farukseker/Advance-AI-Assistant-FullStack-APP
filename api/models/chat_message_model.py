from pydantic import BaseModel


class ChatMessageModel(BaseModel):
    message: str


    def parse_commands(self):
        return self.message
