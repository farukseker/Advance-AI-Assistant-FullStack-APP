import base64
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST, STT_MODEL


class AudioTranscriber:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=STT_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_API_HOST,
        )

    @staticmethod
    def __encode_audio_to_base64(path: Path) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def transcribe(
        self,
        audio_path: Path,
        prompt: str = "Please transcribe this audio file. and dont give any responses about text only transcribe please"
    ):
        base64_audio = self.__encode_audio_to_base64(audio_path)

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": base64_audio,
                        "format": audio_path.suffix.replace(".", ""),
                    },
                },
            ]
        )

        response = self.llm.invoke([message])
        return response.content


# usage
# transcriber = AudioTranscriber(api_key=OPENROUTER_API_KEY)
# text = transcriber.transcribe(Path("audio.wav"))
# print(text)
