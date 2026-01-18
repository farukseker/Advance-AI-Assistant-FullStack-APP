from pydantic import BaseModel


class CreateAudioModel(BaseModel):
    text: str
    voice: str
    rate: int = 0
    volume: int = 0
    pitch: int = 0

    @staticmethod
    def __to_edge_percent(v: int) -> str:
        sign = "+" if v >= 0 else ""
        return f"{sign}{int(v)}%"

    @staticmethod
    def __to_edge_hz(v: int) -> str:
        sign = "+" if v >= 0 else ""
        return f"{sign}{int(v)}Hz"

    def to_dict(self):
        return {
            "text": self.text,
            "voice": self.voice,
            "volume": self.__to_edge_percent(self.volume),
            "rate": self.__to_edge_percent(self.rate),
            "pitch": self.__to_edge_hz(self.pitch),
        }






