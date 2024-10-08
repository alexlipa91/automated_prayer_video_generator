import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Config:

    date: datetime.date
    video_duration_secs: Optional[int]
    output_root: Path

    language: str = "it"

    base_video_path: Path = Path("resources/video/base_video_0.mp4")
    background_music_path: Path = Path(
        "resources/Emotional Love Theme - Biz Baz Studio.mp3")
    thumbnail_base_image_path: Path = Path(
        "resources/previews/pope_sept_2024.png")

    video_file_name: str = "video.mp4"
    transcript_file_name: str = "transcript.txt"
    alignment_file_name: str = "alignment.txt"
    audio_file_name: str = "audio.mp3"
    thumbnail_file_name: str = "thumbnail.png"
    subs_file_name: Optional[str] = "subs.srt"

    subs_block_size_seconds: int = 7

    def __init__(self, date: datetime.date, output_root: str, skip_clean_output_dir: bool = False):
        self.date = date
        self.output_root = Path(output_root).joinpath(
            Path(self.date.strftime("%Y-%m-%d")))

    def init_environment(self):
        # delete the output root if it exists
        if not self.skip_clean_output_dir and self.output_root.exists():
            print(f"Deleting output directory: {self.output_root}")
            shutil.rmtree(self.output_root)
        self.output_root.mkdir(exist_ok=True)

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


def get_config_from_args(args):
    return Config(date=args.date)


# def get_config(language="it"):
#     date_param = sys.argv[1] if len(
#         sys.argv) > 1 else os.environ.get("DATE", None)

#     if not date_param:
#         date_param = datetime.now().strftime("%Y-%m-%d")

#     return Config(date_param, language=language)
