from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import locale
import pprint
import os


@dataclass
class BaseConfig:

    store_firestore_field: str

    public_list_youtube: bool = False
    date: datetime.date = datetime.now().date()

    output_root: Path = Path("output")

    video_duration_secs: Optional[int] = None

    video_file_name: str = "video.mp4"
    transcript_file_name: str = "transcript.txt"
    audio_file_name: str = "audio.mp3"
    thumbnail_file_name: str = "thumbnail.png"
    subs_file_name: str = "subs.srt"
    alignment_file_name: str = "alignment.txt"
    subs_block_size_seconds: int = 3

    def __post_init__(self):
        os.makedirs(self.output_root, exist_ok=True)
        locale.setlocale(locale.LC_ALL, str('it_IT.UTF-8'))

    @property
    def video_path(self) -> Path:
        return self.output_root.joinpath(self.video_file_name)

    @property
    def audio_path(self) -> Path:
        return self.output_root.joinpath(self.audio_file_name)

    @property
    def transcript_path(self) -> Path:
        return self.output_root.joinpath(self.transcript_file_name)

    @property
    def alignment_path(self) -> Path:
        return self.output_root.joinpath(self.alignment_file_name)

    @property
    def subs_path(self) -> Optional[Path]:
        if self.subs_file_name:
            return self.output_root.joinpath(self.subs_file_name)
        return None

    @property
    def thumbnail_path(self) -> Path:
        return self.output_root.joinpath(self.thumbnail_file_name)

    def __str__(self):
        return pprint.pformat(self.__dict__)
