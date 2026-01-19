import shutil
from slugify import slugify
from yt_dlp import YoutubeDL
from pathlib import Path
import tempfile
import atexit
import mimetypes
from dataclasses import dataclass


@dataclass
class MediaData:
    filename: str
    file_dir: str
    file_suffix: str
    path: str
    content_type: str
    data: bytes


class YTDLManager:
    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="ytdl_")
        self.output_dir = Path(self._tmp.name)
        atexit.register(self.__cleanup)

    def __cleanup(self):
        try:
            self._tmp.cleanup()
        except Exception:
            pass


    def download(self, url: str, *, audio=True, srt=True, audio_format="mp3"):
        info = self.__extract_info(url)
        result = []

        if srt and (file := self.__download_subtitle(url, info)):
            result.append(self.__as_data(file))

        if audio and (file := self.__download_audio(url, info, audio_format)):
            result.append(self.__as_data(file))

        if len(result) == 1:
            return result[0]

        return result or None

    @staticmethod
    def __get_node_runtime():
        node_path = shutil.which("node")
        if not node_path:
            raise RuntimeError("Node.js not found in PATH")
        return f"node:{node_path}"

    @staticmethod
    def __extract_info(url: str):
        with YoutubeDL({"quiet": True}) as ydl:
            return ydl.extract_info(url, download=False)

    def __slug_rename(self, info: dict):
        title = slugify(info.get("title", "output"))
        for f in self.output_dir.iterdir():
            new_path = self.output_dir / f"{title}{f.suffix}"
            f.rename(new_path)
            return new_path

    def __download_subtitle(self, url: str, info: dict):
        has_manual = bool(info.get("subtitles"))
        has_auto = bool(info.get("automatic_captions"))

        if not (has_manual or has_auto):
            return None

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": has_manual,
            "writeautomaticsub": not has_manual and has_auto,
            "subtitlesformat": "srt",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return self.__slug_rename(info)

    def __download_audio(self, url: str, info: dict, audio_format: str):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return self.__slug_rename(info)

    def __as_data(self, file: Path) -> MediaData:
        return MediaData(
            filename=file.name,
            file_dir=file.as_posix(),
            file_suffix=file.suffix,
            path=str(file.resolve()),
            content_type=mimetypes.guess_type(file.name)[0] or "application/octet-stream",
            data=file.read_bytes(),
        )