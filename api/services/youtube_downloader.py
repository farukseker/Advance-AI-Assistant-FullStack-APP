import time
import shutil
import mimetypes
import tempfile
import atexit
from pathlib import Path
from dataclasses import dataclass

from slugify import slugify
from yt_dlp import YoutubeDL


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
        atexit.register(self._cleanup)

        self._node = shutil.which("node")
        if not self._node:
            raise RuntimeError("Node.js not found in PATH")

    def _cleanup(self):
        try:
            self._tmp.cleanup()
        except Exception:
            pass

    def download(self, url: str, *, audio=True, srt=True, audio_format="mp3"):
        try:
            info = self._extract_info(url)

            if srt:
                file = self._download_subtitle(url, info)
                if file:
                    return self._as_data(file)

            time.sleep(1)

            if audio:
                file = self._download_audio(url, info, audio_format)
                if file:
                    return self._as_data(file)

            return None

        except Exception as e:
            atexit.unregister(self._cleanup)
            return {
                "error": "ytdlp_unavailable",
                "retryable": True,
                "details": str(e)
            }

    # -------- yt-dlp core --------

    def _base_ydl_opts(self):
        return {
            "quiet": True,
            "ignoreerrors": True,
            "sleep_interval": 2,
            "max_sleep_interval": 5,
            "js_runtimes": {
                "node": {
                    "path": self._node
                }
            },
            "extractor_args": {
                "youtube": {
                    "player_client": ["web"],
                }
            },
        }

    def _extract_info(self, url: str):
        opts = {
            "quiet": True,
            "js_runtimes": {
                "node": {
                    "path": self._node
                }
            }
        }
        with YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def _slug_rename(self, info: dict):
        title = slugify(info.get("title", "output"))
        for f in self.output_dir.iterdir():
            new_path = self.output_dir / f"{title}{f.suffix}"
            f.rename(new_path)
            return new_path
        return None

    # -------- downloads --------

    def _download_subtitle(self, url: str, info: dict):
        has_manual = bool(info.get("subtitles"))
        has_auto = bool(info.get("automatic_captions"))

        if not (has_manual or has_auto):
            return None

        ydl_opts = {
            **self._base_ydl_opts(),
            "skip_download": True,
            "writesubtitles": has_manual,
            "writeautomaticsub": not has_manual and has_auto,
            "subtitlesformat": "srt",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return self._slug_rename(info)

    def _download_audio(self, url: str, info: dict, audio_format: str):
        ydl_opts = {
            **self._base_ydl_opts(),
            "format": "bestaudio/best",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "192",
                }
            ],
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return self._slug_rename(info)

    # -------- output --------

    def _as_data(self, file: Path) -> MediaData:
        return MediaData(
            filename=file.name,
            file_dir=file.as_posix(),
            file_suffix=file.suffix,
            path=file.resolve(),
            content_type=mimetypes.guess_type(file.name)[0]
            or "application/octet-stream",
            data=file.read_bytes(),
        )