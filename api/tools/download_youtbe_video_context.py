from langchain_core.tools import tool
from typing import Annotated
from services import YTDLManager, AudioTranscriber, SRTParser


yt_manager = YTDLManager()

@tool
async def youtube_video_to_into_text_provider(
        youtube_url: Annotated[str, "provide youtube url, youtube.com, youtu.be"]) -> str:
    """
    When a user gives you a YouTube URL, or when you need content from a YouTube video,
    this tool converts the audio from the YouTube video into text.
    A YouTube URL must be provided.
    """
    yt_response = yt_manager.download(youtube_url)
    if isinstance(yt_response, dict):
        raise RuntimeError(
            f"YT-DLP failed: {yt_response.get('details')}"
        )

    if yt_response.file_suffix == ".mp3":
        transcriber = AudioTranscriber()
        return transcriber.transcribe(
            audio_path=yt_response.path,
        )

    srt_parser = SRTParser(
        source=yt_response.path,
    )

    return srt_parser.get_text()