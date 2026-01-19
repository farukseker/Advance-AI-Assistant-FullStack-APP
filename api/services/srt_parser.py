import srt
from pathlib import Path
from typing import Union


class SRTParser:
    def __init__(self, source: Union[str, Path], is_raw: bool = False):
        self.source = Path(source) if not is_raw else source
        self.subtitles = []

    def load(self):
        if isinstance(self.source, Path):
            with self.source.open("r", encoding="utf-8") as f:
                srt_content = f.read()
        else:
            srt_content = self.source
        self.subtitles = list(srt.parse(srt_content))

    def get_text(self):
        return "\n".join([sub.content for sub in self.subtitles])
